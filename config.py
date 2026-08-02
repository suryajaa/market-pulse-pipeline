import os
from dotenv import load_dotenv

load_dotenv()

# --- Google Sheets ---
SHEET_ID = os.environ.get("SHEET_ID")

# --- FRED ---
FRED_API_KEY = os.environ.get("FRED_API_KEY")
FRED_SERIES = ["DGS10", "DGS2", "DGS3MO"]  # 10yr, 2yr, 3mo treasury yields
FRED_DAYS_BACK = 14  # how far back to request observations

# --- Currency (Frankfurter) ---
CURRENCY_BASE = "USD"
CURRENCY_SYMBOLS = ["EUR", "GBP", "JPY", "INR"]

# --- Crypto (CoinGecko) ---
CRYPTO_COINS = ["bitcoin", "ethereum", "solana"]
CRYPTO_VS_CURRENCY = "usd"
