# Laxman Nepal AI Tools

Production AI-tools directory at https://ai.laxmannepal.com.np/

## Architecture

The repository now follows one production path:

```text
data/tools.json
      ↓
scripts/generate_tools.py
      ↓
scripts/build.py
      ↓
tools/index.json + tools/<slug>/ + go/<slug>/
      ↓
scripts/validate.py
      ↓
GitHub Pages
```

### Source of truth

- `data/tools.json` is the canonical published catalog.
- `data/schema.json` defines the catalog contract.
- `scripts/generate_tools.py` is the only catalog generator.
- `scripts/build.py` is the only production build entrypoint.
- `scripts/validate.py` is the deployment gate.
- `tools/` is the canonical public detail-page route.
- `/AItools/` is retired.
- `/go/<slug>/` is the only branded outbound redirect route.

### Build locally

```bash
python -m pip install beautifulsoup4
python scripts/build.py
python scripts/validate.py
```

The build creates the compact homepage index, category metadata, sitemap and robots.txt. Generated pages are deployment artifacts and are not maintained by a second workflow.

## Deployment

`.github/workflows/refresh-ai-tools.yml` is the single build/deploy workflow. It runs on source changes, manual dispatch and the weekly refresh schedule, validates the generated site, then deploys the artifact to GitHub Pages.

The deployment workflow does **not** push generated files back into `main`. This prevents CI loops and keeps generated output separate from source data.
