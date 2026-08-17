from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
BUYERS = DATA_DIR / "buyers.csv"
SENT = DATA_DIR / "sent_log.csv"
BUYER_COLS = ["buyer_name","company_name","email","website","country","source_platform","phone","score"]
SENT_COLS = ["email_address","status","timestamp"]

def _ensure():
    DATA_DIR.mkdir(exist_ok=True)
    if not BUYERS.exists():
        pd.DataFrame(columns=BUYER_COLS).to_csv(BUYERS, index=False)
    if not SENT.exists():
        pd.DataFrame(columns=SENT_COLS).to_csv(SENT, index=False)

def read_buyers():
    _ensure()
    df = pd.read_csv(BUYERS)
    for c in BUYER_COLS:
        if c not in df.columns:
            df[c] = ""
    return df[BUYER_COLS]

def read_sent_log():
    _ensure()
    return pd.read_csv(SENT)

def append_buyers(rows):
    _ensure()
    if not rows:
        return
    old = read_buyers()
    new = pd.DataFrame(rows)
    for c in BUYER_COLS:
        if c not in new.columns:
            new[c] = ""
    merged = pd.concat([old, new[BUYER_COLS]], ignore_index=True)
    merged["email"] = merged["email"].astype(str).str.lower().str.strip()
    merged = merged.drop_duplicates(subset=["email"], keep="first")
    merged.to_csv(BUYERS, index=False)

def already_sent(email):
    log = read_sent_log()
    if log.empty:
        return False
    rows = log[
        (log["email_address"].astype(str).str.lower() == email.lower()) &
        (log["status"].astype(str).str.lower().isin(["sent", "demo-sent"]))
    ]
    return not rows.empty

def log_send(email, status):
    _ensure()
    row = pd.DataFrame([{
        "email_address": email,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }])
    row.to_csv(SENT, mode="a", header=False, index=False)
