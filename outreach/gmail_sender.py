from pathlib import Path
from email.message import EmailMessage
import mimetypes
import smtplib
import ssl
import time
from config import settings
from logging_module.activity_logger import read_buyers, already_sent, log_send

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def _classified_file(audience):
    if audience == "business":
        return DATA_DIR / "business_emails.csv"
    if audience == "individual":
        return DATA_DIR / "individual_emails.csv"
    return None

def _audience_emails(audience):
    if audience == "specific":
        return []
    f = _classified_file(audience)
    if f and f.exists():
        import pandas as pd
        df = pd.read_csv(f)
        if "email_address" in df.columns:
            return sorted(set(df["email_address"].dropna().astype(str).str.lower()))
    df = read_buyers()
    return sorted(set(df["email"].dropna().astype(str).str.lower()))

def _attach(msg, path):
    if not path:
        return
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Attachment not found: {path}")
    ctype, encoding = mimetypes.guess_type(path.name)
    if ctype is None or encoding:
        ctype = "application/octet-stream"
    maintype, subtype = ctype.split("/", 1)
    msg.add_attachment(path.read_bytes(), maintype=maintype,
                       subtype=subtype, filename=path.name)

def send_campaign(subject, body, audience="all", attachment_path=None, specific_emails=None):
    recipients = specific_emails if specific_emails is not None else _audience_emails(audience)
    recipients = [e.strip().lower() for e in recipients if e and not already_sent(e)]

    if not recipients:
        return {"message": "No new recipients are available."}

    recipients = recipients[:settings.daily_send_limit]
    success, failed = [], []

    # Demo mode: lets the college demonstration work without Gmail credentials.
    if not settings.gmail_email or not settings.gmail_app_password:
        df = read_buyers()
        for receiver in recipients:
            log_send(receiver, "demo-sent")
            success.append(receiver)
        return {
            "message": f"Demo mode: {len(success)} email(s) marked as sent. "
                       "Add Gmail credentials to send real emails."
        }

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=30) as smtp:
            smtp.login(settings.gmail_email, settings.gmail_app_password)
            df = read_buyers()
            for receiver in recipients:
                msg = EmailMessage()
                msg["Subject"] = subject
                msg["From"] = settings.gmail_email
                msg["To"] = receiver
                if settings.monitor_email:
                    msg["Cc"] = settings.monitor_email

                personalized = body
                match = df[df["email"].astype(str).str.lower() == receiver]
                if not match.empty:
                    row = match.iloc[0]
                    personalized = personalized.replace(
                        "{{buyer_name}}", str(row.get("buyer_name") or "there")
                    ).replace(
                        "{{company_name}}", str(row.get("company_name") or "")
                    )
                msg.set_content(personalized)

                try:
                    _attach(msg, attachment_path)
                    smtp.send_message(msg)
                    log_send(receiver, "sent")
                    success.append(receiver)
                except Exception:
                    log_send(receiver, "failed")
                    failed.append(receiver)
                time.sleep(max(0, settings.delay))
    except Exception as exc:
        return {"message": f"SMTP connection/login failed: {exc}"}

    return {"message": f"Campaign complete: {len(success)} sent, {len(failed)} failed."}
