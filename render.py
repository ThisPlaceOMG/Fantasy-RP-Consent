"""Render configurable YAML preference sheets as paginated PNGs. No web server."""
import argparse
from pathlib import Path
import re
import yaml
from PIL import Image, ImageDraw, ImageFont, ImageColor

class SheetLoader(yaml.SafeLoader):
    pass
# YAML 1.1 otherwise treats bare yes/no as booleans. Ratings stay text.
SheetLoader.yaml_implicit_resolvers = {
    k: [(tag, pattern) for tag, pattern in values if tag != 'tag:yaml.org,2002:bool']
    for k, values in yaml.SafeLoader.yaml_implicit_resolvers.items()
}

def load_sheet(text):
    return yaml.load(text, Loader=SheetLoader)

ROOT = Path(__file__).resolve().parent
BG='#10151e'; CARD='#19212d'; LINE='#303b4c'; INK='#eef0f5'; MUTED='#a9b3c4'; GOLD='#d8bd86'
W,H=1800,2100
M,GAP,CW=60,24,544
TOP,BOTTOM=340,2010

def font(size,serif=False):
    name='DejaVuSerif-Bold.ttf' if serif else 'DejaVuSans.ttf'
    candidates=[ROOT/'fonts'/name,Path('/usr/share/fonts/truetype/dejavu')/name,Path('C:/Windows/Fonts')/('georgiab.ttf' if serif else 'arial.ttf')]
    for p in candidates:
        if p.exists(): return ImageFont.truetype(str(p),size)
    try: return ImageFont.truetype(name,size)
    except OSError: return ImageFont.load_default(size=size)

CF=font(14); F=font(21); SMALL=font(17); TITLE=font(43,True); HEADING=font(23,True)

def wrap(s,f,width):
    lines=[]
    for paragraph in str(s).split('\n'):
        line=''
        for word in paragraph.split():
            if f.getlength(word)>width:
                # Long unbroken custom labels must not escape their cell.
                chunks=[]; part=''
                for ch in word:
                    if part and f.getlength(part+ch)>width: chunks.append(part);part=''
                    part+=ch
                if part:chunks.append(part)
            else:chunks=[word]
            for chunk in chunks:
                test=(line+' '+chunk).strip()
                if line and f.getlength(test)>width:lines.append(line);line=chunk
                else:line=test
        lines.append(line)
    return lines or ['']

def validate(d):
    if not isinstance(d,dict):raise ValueError('Sheet must be a YAML mapping.')
    for k in ('title','character','server','updated','notes'):
        if k in d and not isinstance(d[k],str):raise ValueError(f'{k} must be text (put dates in quotes).')
        if len(d.get(k,''))>400:raise ValueError(f'{k} must be at most 400 characters.')
    ratings=d.get('ratings')
    if not isinstance(ratings,dict) or not 1<=len(ratings)<=8:raise ValueError('Define 1 to 8 ratings.')
    for code,r in ratings.items():
        if not isinstance(code,str) or not isinstance(r,dict):raise ValueError('Each rating needs a text code and settings.')
        if not all(isinstance(r.get(k),str) for k in ('label','mark','color')):raise ValueError(f'Rating {code} needs label, mark and color.')
        if not 1<=len(r['mark'])<=2 or len(r['label'])>24:raise ValueError('Rating marks: 1–2 characters. Labels: up to 24 characters.')
        ImageColor.getrgb(r['color'])
    cats=d.get('categories')
    if not isinstance(cats,list) or not cats:raise ValueError('Add at least one category.')
    for c in cats:
        if not isinstance(c,dict) or not isinstance(c.get('name'),str):raise ValueError('Category needs a name.')
        cols=c.get('columns');items=c.get('items')
        if not isinstance(cols,list) or not 1<=len(cols)<=3 or not all(isinstance(x,str) for x in cols):raise ValueError(f'{c["name"]}: use 1–3 text column labels.')
        if any(len(x)>40 for x in cols) or len(c['name'])>120:raise ValueError('Category or column label is too long.')
        if not isinstance(items,dict) or not items:raise ValueError(f'{c["name"]}: add items.')
        for name,values in items.items():
            if not isinstance(name,str) or not 1<=len(name)<=300:raise ValueError('Item labels must be 1–300 characters.')
            if not isinstance(values,list) or len(values)!=len(cols):raise ValueError(f'{c["name"]} / {name}: supply {len(cols)} rating code(s).')
            if any(v not in ratings for v in values):raise ValueError(f'{c["name"]} / {name}: unknown code. Choose {", ".join(ratings)}.')
    return d

def layout(c):
    n=len(c['columns']); rw=96 if n<=2 else 82; labelw=CW-32-n*rw
    title=wrap(c['name'],HEADING,CW-32)
    columnlines=[wrap(s,CF,rw-8) for s in c['columns']]
    hh=22+len(title)*29+16+max(map(len,columnlines))*19+14
    rows=[]
    for name,vals in c['items'].items():
        lines=wrap(name,F,labelw-16);rh=max(48,len(lines)*27+18)
        rows.append((lines,vals,rh))
    return rw,labelw,title,columnlines,hh,rows

def render(d,out):
    validate(d);out.mkdir(parents=True,exist_ok=True)
    pages=[]; current=[];col=0;y=TOP
    for c in d['categories']:
        rw,lw,title,cls,hh,rows=layout(c);index=0;cont=False
        # Move whole categories when they fit in an empty column.
        total=hh+sum(row[2] for row in rows)
        if total<=BOTTOM-TOP and y+total>BOTTOM:
            col+=1;y=TOP
            if col==3:pages.append(current);current=[];col=0
        while index<len(rows):
            if y+hh+rows[index][2]>BOTTOM:
                col+=1;y=TOP
                if col==3:pages.append(current);current=[];col=0
            chunk=[];used=hh
            while index<len(rows) and y+used+rows[index][2]<=BOTTOM:
                chunk.append(rows[index]);used+=rows[index][2];index+=1
            current.append((col,y,used,c,rw,lw,title,cls,hh,chunk,cont));y+=used+22;cont=True
    if current:pages.append(current)
    count=sum(len(c['items'])*len(c['columns']) for c in d['categories'])
    answered=sum(v!='unrated' for c in d['categories'] for vs in c['items'].values() for v in vs)
    for pi,blocks in enumerate(pages,1):
        im=Image.new('RGB',(W,H),BG);dr=ImageDraw.Draw(im)
        dr.line((M,48,W-M,48),fill=GOLD,width=2)
        dr.text((M,72),'ROLEPLAY  /  PREFERENCES & BOUNDARIES',font=SMALL,fill=GOLD)
        titlelines=wrap(d.get('character') or 'Unnamed character',TITLE,W-2*M)
        dr.text((M,105),titlelines[0],font=TITLE,fill=INK)
        subtitle='  •  '.join(x for x in [d.get('server'),d.get('title'),d.get('updated')] if x)
        for j,line in enumerate(wrap(subtitle,SMALL,W-2*M)[:2]):dr.text((M,167+j*23),line,font=SMALL,fill=MUTED)
        x=M; yy=229
        for code,r in d['ratings'].items():
            width=48+SMALL.getlength(r['label'])+26
            if x+width>W-M:x=M;yy+=39
            dr.rounded_rectangle((x,yy,x+29,yy+28),radius=6,fill=r['color'])
            dr.text((x+14,yy+14),r['mark'],font=SMALL,fill=BG,anchor='mm')
            dr.text((x+39,yy+3),r['label'],font=SMALL,fill=INK);x+=width
        for j,line in enumerate(wrap(d.get('notes',''),SMALL,W-2*M)[:2]):dr.text((M,289+j*22),line,font=SMALL,fill=MUTED)
        for col,y,height,c,rw,lw,titles,cls,hh,rows,cont in blocks:
            x=M+col*(CW+GAP)
            dr.rounded_rectangle((x,y,x+CW,y+height),radius=12,fill=CARD,outline=LINE,width=1)
            ty=y+15
            for line in titles:dr.text((x+16,ty),line,font=HEADING,fill=GOLD);ty+=29
            if cont:dr.text((x+CW-16,y+8),'cont.',font=font(12),fill=MUTED,anchor='ra')
            cy=ty+12
            for k,lines in enumerate(cls):
                cx=x+16+lw+k*rw+rw/2
                for j,line in enumerate(lines):dr.text((cx,cy+j*19),line,font=CF,fill=MUTED,anchor='ma')
            ry=y+hh
            dr.line((x+16,ry,x+CW-16,ry),fill=LINE)
            for lines,vals,rh in rows:
                for j,line in enumerate(lines):dr.text((x+16,ry+10+j*27),line,font=F,fill=INK)
                for k,code in enumerate(vals):
                    cx=x+16+lw+k*rw+rw/2;my=ry+rh/2;r=d['ratings'][code]
                    dr.rounded_rectangle((cx-18,my-17,cx+18,my+17),radius=7,fill=r['color'])
                    dr.text((cx,my),r['mark'],font=F,fill=BG,anchor='mm')
                ry+=rh
                dr.line((x+16,ry,x+CW-16,ry),fill=LINE)
        dr.line((M,2040,W-M,2040),fill=LINE)
        dr.text((M,2060),f'{answered} / {count} ratings answered  •  Saved character preferences',font=SMALL,fill=MUTED)
        dr.text((W-M,2060),f'{pi} / {len(pages)}',font=SMALL,fill=GOLD,anchor='ra')
        im.save(out/f'page-{pi:02}.png',optimize=True)
    print(f'{len(pages)} PNG pages saved to {out}')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('files',nargs='*');parser.add_argument('--output',default='output');parser.add_argument('--check',action='store_true');args=parser.parse_args()
    files=[Path(x) for x in args.files] if args.files else sorted((ROOT/'sheets').glob('*.y*ml'))
    if not files:parser.error('No YAML sheets found.')
    seen=set()
    for path in files:
        try:
            if path.stat().st_size>2_000_000:raise ValueError('Sheet exceeds 2 MB.')
            d=validate(load_sheet(path.read_text(encoding='utf-8')))
            slug=re.sub(r'[^a-zA-Z0-9_-]+','-',path.stem).strip('-') or 'sheet'
            if slug in seen:raise ValueError('Duplicate output filenames; rename one sheet.')
            seen.add(slug)
            if args.check:print(f'Valid: {path}')
            else:render(d,Path(args.output)/slug)
        except (ValueError,KeyError,TypeError,yaml.YAMLError) as e:parser.exit(1,f'{path}: {e}\n')

if __name__=='__main__':main()
