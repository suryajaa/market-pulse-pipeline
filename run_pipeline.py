import os
from datetime import datetime, timezone

import pandas as pd

import config
from fetch import fetch_frankfurter, fetch_coingecko, fetch_fred
from sheets_writer import write_tab, update_status_tab


def _now():
    return datetime.now(timezone.utc).isoformat()


def _log_success(status_rows, source, detail):
    status_rows.append({"source": source, "status": "success", "detail": detail, "timestamp": _now()})


def _log_failure(status_rows, source, error):
    status_rows.append({"source": source, "status": "fail", "detail": str(error), "timestamp": _now()})


def write_log_file(status_rows, path="logs/latest_run.log"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(f"Market Pulse Pipeline run: {_now()}\n\n")
        for row in status_rows:
            f.write(f"[{row['status'].upper()}] {row['source']}: {row['detail']} ({row['timestamp']})\n")


def run():
    status_rows = []

    # --- Currency ---
    try:
        df = fetch_frankfurter(base=config.CURRENCY_BASE, symbols=config.CURRENCY_SYMBOLS)
        write_tab(config.SHEET_ID, "Currency", df)
        _log_success(status_rows, "frankfurter", f"{len(df)} rows")
    except Exception as e:
        _log_failure(status_rows, "frankfurter", e)

    # --- Crypto ---
    try:
        df = fetch_coingecko(coins=config.CRYPTO_COINS, vs_currency=config.CRYPTO_VS_CURRENCY)
        write_tab(config.SHEET_ID, "Crypto", df)
        _log_success(status_rows, "coingecko", f"{len(df)} rows")
    except Exception as e:
        _log_failure(status_rows, "coingecko", e)

    # --- Macro (FRED) ---
    try:
        frames = [
            fetch_fred(series_id=series_id, days_back=config.FRED_DAYS_BACK, api_key=config.FRED_API_KEY)
            for series_id in config.FRED_SERIES
        ]
        combined = pd.concat(frames, ignore_index=True)
        write_tab(config.SHEET_ID, "Macro", combined)
        _log_success(status_rows, "fred", f"{len(combined)} rows across {len(config.FRED_SERIES)} series")
    except Exception as e:
        _log_failure(status_rows, "fred", e)

    # --- Status tab always updates, regardless of the above ---
    try:
        update_status_tab(config.SHEET_ID, status_rows)
    except Exception as e:
        print(f"WARNING: failed to write status tab: {e}")

    write_log_file(status_rows)

    print("Pipeline run complete.")
    for row in status_rows:
        print(f"  [{row['status'].upper()}] {row['source']}: {row['detail']}")


if __name__ == "__main__":
    run()
