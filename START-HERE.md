# Start here

## Server owner: first setup

1. Unzip the download on your computer.
2. On GitHub, choose **New repository**, give it a name, and choose public or private. Do not add a README yet.
3. Upload the **contents** of this folder to the repository root. You should see `README.md`, `render.py`, `sheets/`, and `template.yml` at the top level, not inside another folder.
4. The ZIP includes a hidden `.github` folder. Some file managers hide it. If it did not upload, use **Add file → Create new file**, name the file `.github/workflows/render.yml`, and paste the contents of `WORKFLOW-COPY.txt` into it. Commit the new file. That creates the exact required hidden folder and workflow.
5. Edit `template.yml` with your server's question list. Also replace `sheets/my-character.yml` with your customized blank template.
6. Open **Settings → General → Template repository** and enable it if you want players to use **Use this template → Create a new repository**. They should select **Private** when creating their copy if answers should stay private.
7. Share the template repository link with players. They should create copies, not request editing access to your master.

For a private master, players need repository access to use it. A public blank master with private player copies is usually simpler. The distributed package includes broad adult kink terms and fictional dark themes; keep content consistent with the host's rules.

## Player: fill out your copy

1. Create your own repository from the server's template. Choose **Private** if you do not want working answers visible.
2. Open `sheets/my-character.yml` and click the pencil (**Edit this file**).
3. Enter your character name and server at the top.
4. Replace answers such as `[unrated, unrated]` with `[yes, discuss]`. Read the category's `columns` line to see which answer is which.
5. Choose **Commit changes** to save. No Python installation is required on your computer.
6. Open **Actions**. If GitHub asks you to enable workflows in your own copy, enable them.
7. Select **Make consent sheet pictures → Run workflow**. Wait for the green check.
8. Open the completed run. Scroll to **Artifacts** and download **completed-consent-sheets**.
9. Unzip the download and share the PNG pages on Discord. Keep your YAML file to edit answers later.

## Example

```yaml
character: Astoria
server: Fantasy RP
updated: '2026-10-31'
```

```yaml
- name: Praise and Degradation
  columns: [Giving, Receiving]
  items:
    Gentle Praise: [yes, favorite]
    Public Humiliation: [no, discuss]
```

These answers are examples only.

## If something goes wrong

- **No Actions workflow:** confirm `.github/workflows/render.yml` exists on the default branch. `WORKFLOW-COPY.txt` alone does not run.
- **A red X:** open the failed workflow, then **Validate and render sheets**. The error identifies the question with a wrong code or answer count. Fix the YAML and commit again.
- **No pictures:** edit a file inside `sheets/`, not just `template.yml`, or run the workflow manually.
- **Code displays as invalid:** use exactly `unrated`, `no`, `discuss`, `yes`, or `favorite`, unless your template defines different codes.
- **Wrong number of answers:** one answer per column. Giving/Receiving needs two; General needs one.
- **An old download disappeared:** artifacts expire after 30 days. Run the workflow again from your saved sheet.
- **Need to change the questions later:** edit the sheet itself. Updating the master doesn't replace existing answers automatically.
