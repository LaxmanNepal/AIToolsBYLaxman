# Laxman Nepal AI Tools

Production AI-tools directory: https://ai.laxmannepal.com.np/

## Architecture

```text
data/tools.json                         ← canonical source of truth
        ↓
scripts/generate_tools.py              ← normalize + generate detail/redirect pages
        ↓
scripts/build.py                      ← production build
        ↓
tools/index.json                      ← lightweight discovery index
categories/<slug>/                      ← crawlable category landing pages
tools/<slug>/                           ← canonical detail pages
go/<slug>/                              ← noindex branded outbound routes
sitemap.xml + robots.txt
        ↓
scripts/validate.py                   ← structural/data deployment gate
scripts/check_links.py                  ← provider URL health gate
        ↓
GitHub Pages public artifact only
```

## Product features

- Lightweight catalog discovery index instead of shipping the 8 MB source dataset to browsers.
- Search with debounce, typo tolerance and autocomplete.
- Pagination instead of rendering the whole catalog at once.
- Category counts and crawlable category URLs.
- Free/Freemium/Paid filtering and sorting.
- Local favorites using browser storage.
- Three-tool comparison page.
- Dedicated search route.
- Trending and GitHub views use the canonical public index.
- Dedicated tool pages with canonical URLs, Open Graph metadata, breadcrumbs, related tools and structured data.
- PWA with network-first catalog refresh and offline homepage fallback.

## Data contract

`data/tools.json` is the only published catalog source. `data/schema.json` documents required fields including pricing, verification state, lifecycle status, supported platforms and languages.

Important: a generated `lastVerified` date is a catalog-record date, not proof that pricing or product claims were manually verified. `scripts/check_links.py` independently checks provider URLs during deployment.

## Quality gates

```bash
python scripts/build.py
python scripts/validate.py
python scripts/check_links.py
```

The build refuses catalogs below 500 valid tools, rejects malformed routes/URLs/metadata, prevents duplicate slugs and duplicate provider URLs, and verifies every generated detail and redirect page.

The link checker performs concurrent provider URL checks and blocks deployment when more than 25% of providers fail. Its report is generated as `link-report.json` in CI.

## Deployment

There is one GitHub Actions workflow: `.github/workflows/refresh-ai-tools.yml`.

It builds from the canonical dataset, validates the generated site, checks provider links, stages only public files into `_site`, and deploys that artifact to GitHub Pages. It does **not** commit generated pages back to `main`, preventing CI loops and keeping source data separate from deployment artifacts.

## Retired architecture

The following concepts are intentionally retired:

- `/AItools/`
- `Scripts/` vs `scripts/` duplication
- `everything.json`
- `ToolList.txt`
- competing catalog generators
- browser-side API-key architecture
- duplicate deployment workflows

## Contributing

Change the canonical catalog or build scripts, then run all three quality gates before merging. Do not add another generator or another catalog file.
