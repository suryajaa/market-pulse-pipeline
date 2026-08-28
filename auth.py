import os
import json

from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_credentials():
    raw_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not raw_json:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON environment variable is not set.")

    try:
        info = json.loads(raw_json)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON: {e}")

    return Credentials.from_service_account_info(info, scopes=SCOPES)
