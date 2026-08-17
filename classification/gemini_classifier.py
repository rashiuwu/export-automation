from pathlib import Path
import csv
from config import settings
from logging_module.activity_logger import read_buyers

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
BUSINESS_FILE = DATA_DIR / "business_emails.csv"
INDIVIDUAL_FILE = DATA_DIR / "individual_emails.csv"

def _write(path, emails):
    path.parent.mkdir(exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["email_address"])
        for e in sorted(set(emails)):
            w.writerow([e])

def classify_emails():
    df = read_buyers()
    if df.empty:
        return {"message": "No buyer records to classify."}

    emails = sorted(set(df["email"].dropna().astype(str).str.lower()))
    if not emails:
        return {"message": "No email addresses found."}

    labels = {}
    if settings.gemini_api_key:
        try:
            from google import genai
            client = genai.Client(api_key=settings.gemini_api_key)
            prompt = (
                "Classify each email as business or individual. Return ONLY CSV lines "
                "email,label. No markdown. Business means a company/organization address; "
                "individual means a personal mailbox.\n" + "\n".join(emails)
            )
            response = client.models.generate_content(
                model=settings.gemini_model, contents=prompt
            )
            for line in response.text.splitlines():
                parts = [p.strip() for p in line.split(",", 1)]
                if len(parts) == 2 and parts[0].lower() in emails:
                    labels[parts[0].lower()] = (
                        "business" if parts[1].lower().startswith("business") else "individual"
                    )
        except Exception:
            labels = {}

    business, individual = [], []
    personal_domains = {
        "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
        "icloud.com", "proton.me", "protonmail.com"
    }
    for email in emails:
        label = labels.get(email)
        if not label:
            domain = email.split("@")[-1]
            label = "individual" if domain in personal_domains else "business"
        (business if label == "business" else individual).append(email)

    _write(BUSINESS_FILE, business)
    _write(INDIVIDUAL_FILE, individual)
    return {"message": f"Classified {len(emails)} emails: {len(business)} business, {len(individual)} individual."}
