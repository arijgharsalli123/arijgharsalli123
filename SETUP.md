# Arij's free GitHub Solar System — setup

This project generates `assets/solar-system.svg` from your public GitHub repositories and language statistics. It uses Python's standard library only; no paid API or third-party image service is required.

## 1. Put the files in your profile repository

Your profile repository must be named exactly after your GitHub username:

`arijgharsalli123/arijgharsalli123`

Copy these into the repository:
- `scripts/generate_solar_system.py`
- `.github/workflows/solar-system.yml`
- `assets/` (the workflow will create `solar-system.svg`)
- Add the image embed from `README-SOLAR-SYSTEM-SECTION.md` to your existing README.

Do not replace your whole existing README unless you want to. Put the Solar System section wherever you want the graphic to appear.

## 2. Enable workflow write permissions

On GitHub:
1. Open your profile repository.
2. Go to **Settings → Actions → General**.
3. Under **Workflow permissions**, select **Read and write permissions**.
4. Save.

The workflow uses GitHub's built-in `GITHUB_TOKEN`; no personal access token is required for a typical profile with fewer than 60 public repositories. The workflow token has repository-scoped permissions.

## 3. Run it once

Open **Actions → Update GitHub Solar System → Run workflow**.

The workflow:
- Reads your public repositories.
- Collects language byte counts.
- Downloads your GitHub avatar and embeds it in the SVG.
- Creates or updates `assets/solar-system.svg`.
- Commits the generated file to your profile repository.

It also runs every 12 hours and after changes to the generator or workflow.

## 4. Local preview (optional)

Python 3.10+ is sufficient:

```bash
GITHUB_USERNAME=arijgharsalli123 python scripts/generate_solar_system.py
```

On Windows PowerShell:

```powershell
$env:GITHUB_USERNAME = "arijgharsalli123"
python scripts/generate_solar_system.py
```

Then open `assets/solar-system.svg` in a browser.

## Notes and customization

- This is a generated static SVG, not an animated interactive webpage. It is compatible with GitHub README rendering.
- Repository language percentages are calculated from GitHub's language API byte counts, not from subjective skill levels.
- Only non-fork, non-archived public repositories are included.
- The generator currently analyzes up to 60 recently updated repositories to limit API requests.
- The SVG displays up to seven languages and six recently updated repositories.
- GitHub Actions schedules can start a little later than the exact cron time.
- The GitHub profile README must be in the repository named exactly `arijgharsalli123`.
