import gspread

from auth import get_credentials


def _get_client():
    creds = get_credentials()
    return gspread.authorize(creds)


def write_tab(sheet_id, tab_name, dataframe):
    """Overwrite (or create) a tab with the contents of a DataFrame."""
    client = _get_client()
    spreadsheet = client.open_by_key(sheet_id)

    try:
        worksheet = spreadsheet.worksheet(tab_name)
        worksheet.clear()
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=tab_name, rows=200, cols=20)

    values = [dataframe.columns.tolist()] + dataframe.astype(str).values.tolist()
    worksheet.update(values)


def update_status_tab(sheet_id, status_rows, tab_name="Status"):
    """
    Always-updating status tab, independent of whether individual sources
    succeeded or failed.

    status_rows: list of dicts like
        {"source": "frankfurter", "status": "success", "detail": "4 rows", "timestamp": "..."}
    """
    client = _get_client()
    spreadsheet = client.open_by_key(sheet_id)

    try:
        worksheet = spreadsheet.worksheet(tab_name)
        worksheet.clear()
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=tab_name, rows=20, cols=10)

    header = ["source", "status", "detail", "timestamp"]
    rows = [header]
    for row in status_rows:
        rows.append([
            row.get("source", ""),
            row.get("status", ""),
            row.get("detail", ""),
            row.get("timestamp", ""),
        ])
    worksheet.update(rows)
