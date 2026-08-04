import os
from datetime import datetime, timedelta, timezone

import requests
import pandas as pd


def fetch_frankfurter(base="USD", symbols=None):
    """Fetch latest currency exchange rates from Frankfurter"""
    symbols = symbols or ["EUR", "GBP", "JPY", "INR"]
    url = "https://api.frankfurter.app/latest"
    params = {"from": base, "to": ",".join(symbols)}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Frankfurter request failed: {e}")

    data = response.json()
    rates = data.get("rates")
    if not rates:
        raise RuntimeError("Frankfurter response missing 'rates' field.")

    fetched_at = datetime.now(timezone.utc).isoformat()
    rows = [
        {"base": base, "currency": currency, "rate": rate, "fetched_at": fetched_at}
        for currency, rate in rates.items()
    ]
    return pd.DataFrame(rows)


def fetch_coingecko(coins=None, vs_currency="usd"):
    """Fetch current crypto prices + 24h change from CoinGecko"""
    coins = coins or ["bitcoin", "ethereum", "solana"]
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ",".join(coins),
        "vs_currencies": vs_currency,
        "include_24hr_change": "true",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"CoinGecko request failed: {e}")

    data = response.json()
    if not data:
        raise RuntimeError("CoinGecko response was empty.")

    fetched_at = datetime.now(timezone.utc).isoformat()
    change_key = f"{vs_currency}_24h_change"
    rows = []
    for coin_name, price_info in data.items():
        price = price_info.get(vs_currency)
        if price is None:
            raise RuntimeError(f"CoinGecko response missing price for '{coin_name}'.")
        change = price_info.get(change_key)
        rows.append({
            "coin": coin_name,
            "price": price,
            "change_24h_pct": round(change, 2) if change is not None else None,
            "fetched_at": fetched_at,
        })
    return pd.DataFrame(rows)


def fetch_fred(series_id="DGS10", days_back=14, api_key=None):
    """ Fetch recent observations for a FRED series """
    api_key = api_key or os.environ.get("FRED_API_KEY")
    if not api_key:
        raise RuntimeError("FRED_API_KEY is not set.")

    start_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%d")

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start_date,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"FRED request failed for series '{series_id}': {e}")

    data = response.json()
    observations = data.get("observations")
    if observations is None:
        raise RuntimeError(f"FRED response missing 'observations' field for series '{series_id}'.")

    fetched_at = datetime.now(timezone.utc).isoformat()
    rows = []
    for obs in observations:
        raw_value = obs.get("value")
        if raw_value is None or raw_value == ".":
            continue  
        try:
            value = float(raw_value)
        except ValueError:
            continue  
        rows.append({
            "series_id": series_id,
            "date": obs.get("date"),
            "value": value,
            "fetched_at": fetched_at,
        })

    if not rows:
        raise RuntimeError(
            f"No usable observations returned for '{series_id}' in the last {days_back} days."
        )

    return pd.DataFrame(rows)
