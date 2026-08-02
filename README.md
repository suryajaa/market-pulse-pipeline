# Market Pulse Pipeline

An automated data pipeline that pulls daily market data from three independent
public APIs, transforms it, and writes it into a shared Google Sheet dashboard
on a schedule via GitHub Actions.

**Sources:**
| Source | Data | Auth |
|---|---|---|
| [Frankfurter](https://www.frankfurter.app/) | Currency exchange rates | None |
| [CoinGecko](https://www.coingecko.com/en/api) | Crypto prices + 24h change | None |
| [FRED](https://fred.stlouisfed.org/docs/api/fred/) | Treasury yields (macro rates) | Free API key |

## Why this project

Built to demonstrate a small but realistic data engineering pattern: multiple
external sources with different auth/shape/failure characteristics, isolated
error handling per source, credential management that works identically
locally and in CI, and a scheduled, unattended run.

## Architecture

```
config.py         # env-driven settings (sheet ID, API keys, series/coins to track)
auth.py           # loads Google service account credentials from an env var
fetch.py          # one function per source; each raises on failure (never returns None)
sheets_writer.py  # write_tab() + update_status_tab()
run_pipeline.py   # orchestrator: wraps each source in its own try/except
```

**Design decisions worth calling out:**

- **Fail-loud fetch functions.** Each `fetch_*` function raises an exception on
  failure instead of returning `None` or an empty result. Silent `None`
  returns push error-checking onto every caller and are easy to forget;
  raising forces the orchestrator to handle failure explicitly.
- **Per-source isolation.** `run_pipeline.py` wraps each source's fetch +
  write in its own `try/except`, so if (say) FRED is down or rate-limited,
  currency and crypto still update normally.
- **Always-updating status tab.** A dedicated `Status` tab records
  success/fail + timestamp for every source on every run, regardless of
  individual failures — so a glance at the Sheet tells you what's fresh and
  what isn't, without digging through logs.
- **One credential-loading path.** Google credentials are read from a single
  `GOOGLE_SERVICE_ACCOUNT_JSON` env var — no "if running locally, read a file;
  if running in CI, read a secret" branching. Locally it comes from `.env`
  (via `python-dotenv`); in GitHub Actions it comes from a repo secret. Same
  code either way.
- **Least privilege.** The service account only has access to the one Sheet
  it was explicitly shared with — not the whole Drive.

## Setup

1. Clone the repo and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in:
   - `GOOGLE_SERVICE_ACCOUNT_JSON` — full service account JSON as one line
   - `SHEET_ID` — the ID from your Google Sheet's URL
   - `FRED_API_KEY` — free key from FRED
3. Share the target Google Sheet with the service account's email address
   (found in the JSON as `client_email`), with Editor access.
4. Run it:
   ```bash
   python run_pipeline.py
   ```

## Scheduling (GitHub Actions)

`.github/workflows/pipeline.yml` runs the pipeline daily at 12:00 UTC and can
also be triggered manually from the Actions tab. It requires the same three
values above set as **repository secrets** (Settings → Secrets and variables
→ Actions).

## A note on durability (why this repo has committed logs)

Live dashboards are fragile as portfolio artifacts — if a reviewer looks at
this repo after the free-tier API key has expired, the Sheet has been
unshared, or GitHub Actions has been paused for inactivity, a "check the live
Sheet" pitch falls flat. To make this project's track record durable
independent of the live pipeline, each scheduled run **commits its status log
back into the repo** at `logs/latest_run.log`. That gives anyone reviewing the
project a real, timestamped history of runs directly in the commit log, with
no live dependency required.

## Status

- [x] Currency, crypto, and macro fetch functions
- [x] Google Sheets writer + status tab
- [x] Orchestrator with per-source error isolation
- [x] GitHub Actions scheduling
- [ ] Screenshots of the live dashboard (add here once a few days of runs have accumulated)
