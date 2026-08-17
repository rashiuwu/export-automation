from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

from config import settings
from extraction.data_extractor import normalize_rows
from validation.email_validator import validate_email
from logging_module.activity_logger import (
    append_buyers, read_buyers, read_sent_log, already_sent, log_send
)
from outreach.gmail_sender import send_campaign

bp = Blueprint("main", __name__)

def _lead_df():
    df = read_buyers()
    for col, default in {
        "buyer_name": "", "company_name": "", "email": "", "website": "",
        "country": "", "source_platform": "", "phone": "", "score": 0
    }.items():
        if col not in df.columns:
            df[col] = default
    sent = read_sent_log()
    contacted = set()
    if not sent.empty:
        contacted = set(
            sent.loc[sent["status"].astype(str).str.lower().isin(["sent", "demo-sent"]),
                     "email_address"].astype(str).str.lower()
        )
    df["contacted"] = df["email"].astype(str).str.lower().isin(contacted)
    return df

def stats():
    buyers = _lead_df()
    sent = read_sent_log()
    total = len(sent)
    success = int(sent["status"].astype(str).str.lower().isin(["sent", "demo-sent"]).sum()) if not sent.empty else 0
    failed = int((sent["status"].astype(str).str.lower() == "failed").sum()) if not sent.empty else 0
    rate = round(success / total * 100, 2) if total else 0
    return len(buyers), total, success, failed, rate

@bp.get("/")
def home():
    return render_template("home.html", stats=stats(), leads=_lead_df().to_dict("records"))

@bp.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        f = request.files.get("file")
        if not f or not f.filename.lower().endswith(".csv"):
            flash("Please upload a CSV file.")
            return redirect(url_for("main.upload"))
        df = pd.read_csv(f)
        rows = normalize_rows(df.to_dict("records"), source="CSV Upload")
        valid = []
        for r in rows:
            if validate_email(r.get("email", "")):
                original = next(
                    (x for x in df.to_dict("records")
                     if str(x.get("email") or x.get("email_address") or "").strip().lower()
                     == r["email"]), {}
                )
                r["phone"] = original.get("phone", original.get("phone_number", ""))
                r["score"] = original.get("score", 100)
                valid.append(r)
        append_buyers(valid)
        flash(f"Imported {len(valid)} valid buyer records.")
        return redirect(url_for("main.home"))
    return render_template("upload.html")

@bp.post("/classify")
def classify():
    from classification.gemini_classifier import classify_emails
    result = classify_emails()
    flash(result["message"])
    return redirect(url_for("main.home"))

@bp.route("/send", methods=["GET", "POST"])
def send():
    if request.method == "POST":
        subject = request.form.get("subject", "").strip()
        body = request.form.get("body", "").strip()
        audience = request.form.get("audience", "all")
        attachment = request.files.get("attachment")
        attachment_path = None

        if attachment and attachment.filename:
            ASSETS_DIR.mkdir(exist_ok=True)
            attachment_path = ASSETS_DIR / attachment.filename
            attachment.save(attachment_path)

        if not subject or not body:
            flash("Subject and body are required.")
            return redirect(url_for("main.send"))

        result = send_campaign(subject, body, audience, attachment_path)
        flash(result["message"])
        return redirect(url_for("main.home"))
    return render_template("send.html")

@bp.post("/send-lead/<path:email>")
def send_lead(email):
    df = _lead_df()
    match = df[df["email"].astype(str).str.lower() == email.lower()]
    if match.empty:
        flash("Lead not found.")
        return redirect(url_for("main.home"))

    row = match.iloc[0]
    if already_sent(email):
        flash(f"{email} has already been contacted.")
        return redirect(url_for("main.home"))

    subject = request.form.get("subject", "Singing Bowls Export Presentation")
    body = request.form.get(
        "body",
        "Hello {{buyer_name}},\n\nWe would like to introduce our Singing Bowls export collection. "
        "Please find our company presentation attached.\n\nRegards,\nExport Team"
    )

    result = send_campaign(subject, body, "specific", None, specific_emails=[email])
    flash(result["message"])
    return redirect(url_for("main.home"))

@bp.post("/delete-lead/<path:email>")
def delete_lead(email):
    buyers = read_buyers()
    buyers = buyers[buyers["email"].astype(str).str.lower() != email.lower()]
    buyers.to_csv(DATA_DIR / "buyers.csv", index=False)
    flash(f"Deleted {email}.")
    return redirect(url_for("main.home"))

@bp.get("/report")
def report():
    buyers, total, success, failed, rate = stats()
    sent = read_sent_log()
    rows = sent.tail(100).to_dict("records") if not sent.empty else []
    return render_template("report.html", buyers=buyers, total=total,
                           success=success, failed=failed, rate=rate, rows=rows)

@bp.get("/settings")
def settings_page():
    return render_template("settings.html", config={
        "email": settings.gmail_email,
        "daily_send_limit": settings.daily_send_limit,
        "search_keyword": settings.search_keyword,
        "delay": settings.delay,
    })

@bp.get("/download-report")
def download_report():
    DATA_DIR.mkdir(exist_ok=True)
    src = DATA_DIR / "sent_log.csv"
    if not src.exists():
        pd.DataFrame(columns=["email_address", "status", "timestamp"]).to_csv(src, index=False)
    return send_file(src, as_attachment=True, download_name="campaign_report.csv")
