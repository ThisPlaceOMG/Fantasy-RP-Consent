# Fantasy Roleplay Consent Sheets

An editable GitHub template that generates shareable PNG pictures. No website, server or bot. Includes 27 categories and 239 items; Pregnancy and Family Themes is excluded.

**Start with `START-HERE.md`.** The preview folder shows a fictional example, not anyone's preferences.

## Your files

| File | Purpose |
| --- | --- |
| `template.yml` | Blank master you customize and distribute. |
| `sheets/my-character.yml` | Player's working sheet. This is what the workflow renders. |
| `render.py` | Turns sheets into paginated PNGs. |
| `.github/workflows/render.yml` | Runs automatically after sheet edits, or manually. |
| `preview/sample/` | Example output with deliberately mixed sample ratings. |

## Fill out answers

Edit `sheets/my-character.yml`. Change character/server at the top. Replace `unrated` beside each question with:

| Code | Meaning |
| --- | --- |
| `unrated` | Not answered; never interpreted as permission |
| `no` | No |
| `discuss` | Discuss first |
| `yes` | Yes |
| `favorite` | Favorite |

The column order controls the answer order:

```yaml
- name: Power Exchange
  columns: [As Dominant, As Submissive]
  items:
    Commands / Obedience: [yes, discuss]
    Switching Roles: [no, no]
```

One-column categories need one answer: `Slow-Burn Romance: [favorite]`.
Bare `yes` and `no` are supported by this renderer. Keep square brackets, commas and indentation. Use spaces, not tabs.

## Configure the list

Edit `template.yml` to create your master. Add/remove/reorder categories and questions by moving their blocks. Each category has `name`, `columns` (1–3 labels), and `items` (question labels mapped to one code per column). Duplicate a category block to add one. Question labels must be unique within their category.

Use quotes around text with a colon, for example `"Courtship: Public": [discuss]`.

Change `ratings` to edit labels, letters and hex colors. The renderer supports up to 8 codes, with 1–2-character symbols. If you rename a code, update answers that use it. The special code `unrated` is used for the answered counter; keep it for unanswered items.

Changes to the master do **not** overwrite existing character sheets. Copy the updated master into `sheets/` for new sheets; merge question changes into completed sheets manually to preserve answers. In your initial distribution, update both the master and blank working sheet.

No default answer is consent. Ratings describe preferences; the specific scene still needs agreement and must follow server rules.

## Generate pictures

Save changes under `sheets/` on GitHub. Open **Actions → Make consent sheet pictures → latest successful run**. Under **Artifacts**, download `completed-consent-sheets` and unzip it. Each character has a folder of numbered PNG pages. Share all pages for a complete sheet.

For manual generation: **Actions → Make consent sheet pictures → Run workflow**. The workflow must be on the repository's default branch. No files are automatically published or committed back. Artifacts are retained for 30 days; download copies to keep. GitHub usage allowances apply to private repositories.

To regenerate, edit the same YAML file and save another commit. To add a second character, copy the template into `sheets/another-character.yml`. Filenames must be unique.

## Optional local use

With Python 3.12 or newer installed:

```sh
python -m pip install -r requirements.txt
python render.py
```

Pictures appear in `output/`. Validate without rendering: `python render.py --check`. Render one file: `python render.py sheets/my-character.yml`. The renderer uses DejaVu fonts on GitHub Linux; local systems can fall back to installed fonts.

## Privacy

A public repository exposes committed character answers and earlier versions. Each player should create their **own private repository** if they want private working answers. Only share the downloaded PNGs they intend others to see. Making a later edit does not erase Git history.

A GitHub account is needed to edit/run your own repository; image recipients need no account. There is no clickable questionnaire: players edit rating codes in a text file. No analytics, accounts database or external AI service is used by the renderer.
