# AGENTS.md

Repo that scrapes Chadstone Shopping Centre parking occupancy + 7-day traffic forecast every
30 minutes and commits CSVs to this repo for public analysis. Default branch is **master**.

## Entrypoints

- `scripts/scrape.py` — the production scraper (called by GitHub Actions every 30 min)
- `scripts/generate_charts.py` — regenerates all 10 HTML charts in `charts/`
- `main.py` is a scaffold stub — ignore it
- `notebooks/chart_parking.ipynb` — analysis notebook; its last cell shells out to `uv run` to regenerate charts

## Commands

- `python scripts/scrape.py` — run one scrape. Stdlib-only, but **requires `curl` on PATH** (deliberate: subprocess curl bypasses TLS fingerprinting — do NOT refactor to requests/httpx). Appends to `data/parking.csv` and `data/traffic.csv`.
- `uv run python scripts/generate_charts.py` — regenerate charts. **Needs network**: it loads data from the raw GitHub CSV on the `master` branch (`DATA_URL` at top of file), not from local `data/`. To test with local data, point `DATA_URL` at the local file first.
- No tests, linters, or formatters are configured; verifying = running the scripts.

## Data

- `data/parking.csv` / `data/traffic.csv` are append-only, bot-committed datasets (`chaddy-scraper[bot]`). Don't hand-edit them; the scraper owns them.
- Timestamps are AEST (UTC+10), format `%Y-%m-%d %H:%M:%S`.
- Traffic `occupancy` can exceed 1.0 on peak days; `alert_level` is GREEN/YELLOW/RED.
- Car park D is private — only A, B, C, E, F appear.

## Charts

- `charts/chart1_lines.html` … `chart10_heatmap.html` are the canonical generated set (self-contained HTML via the `xy` package).
- `charts/carpark_b.html` and `charts/total_occupancy.html` are legacy notebook-era files — don't touch.
- `charts/index.html` is a static landing page linking the 10 charts.
- New charts should reuse the shared style constants (`_TIP`, `_CHART_CLASS`, `_PALETTE`, `_QUIET` helpers) at the top of `generate_charts.py`.
- Live charts are served at <https://jay-stein.github.io/chaddy-parking-scraper/> — deployed by `.github/workflows/charts-pages.yml` after every successful scrape (no git commits involved).

## CI / Environment

- `.github/workflows/scrape.yml` runs `python scrape.py` with Python 3.12 and **no dependency install** (scrape.py is stdlib-only). It auto-commits `data/` changes and pushes to master.
- `.github/workflows/charts-pages.yml` regenerates charts from the fresh local `data/parking.csv` (`CHARTS_DATA_URL` env var) and deploys them to GitHub Pages via `workflow_run` on the scrape workflow + `workflow_dispatch`.
- Local dev: uv-managed Python 3.14 (`.python-version`), deps `polars` + `xy`, dev group `jupyter`.
- The built-in `schedule` cron is a best-effort fallback; the real trigger is an external cron using `workflow_dispatch`.

## Git

- Branch from `master` as `agent/<short-task-name>`; never push directly to master (the scrape bot is the exception).
- Conventional Commits (`feat(charts): …`, `chore: scrape …`, `docs(readme): …`).
