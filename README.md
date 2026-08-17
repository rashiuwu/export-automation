# API 3 — EXPORT Automation System

A Flask-based implementation of the documented EXPORT Automation pipeline for Singing Bowls export outreach.

## Pipeline

Buyer records → validation → AI classification → duplicate check → Gmail SMTP campaign → CSV logging/report.

The architecture follows the supplied documentation: separate discovery, extraction/validation, outreach, and reporting layers, with CSV files as the local data store.

## 1. Setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
```

Edit `.env`.

For Gmail SMTP, enable 2-Step Verification and create an App Password. Do not put your normal Gmail password in `.env`.

## 2. Run

```bash
python main.py
```

Open http://127.0.0.1:5000

## 3. Lead CSV

Example:

```csv
buyer_name,company_name,email,website,country,source_platform
Jane,Example Imports,jane@example.com,https://example.com,USA,CSV Upload
```

## 4. AI classification

Set `GEMINI_API_KEY` to enable Gemini classification. If it is empty, the app uses a small personal-domain fallback so the rest of the system can be tested.

## 5. Discovery adapters

`search/google_search.py` is wired for Google Custom Search JSON API using `GOOGLE_API_KEY` and `GOOGLE_CSE_ID`.

Facebook, LinkedIn, and directory adapters are intentionally provider/API placeholders. Replace them with authorized APIs or licensed data providers rather than scraping restricted services.

## 6. Important safety/operations notes

- Test campaigns using your own addresses before contacting anyone else.
- Use only contacts and data you are authorized to use.
- Add consent/unsubscribe/compliance controls before production commercial email.
- Keep `.env` out of Git.
- The documentation identifies missing authentication, consent management, and production-scale database support as limitations/future improvements.

## Main files

- `main.py` — entry point
- `config.py` — configuration
- `app/routes.py` — web interface
- `extraction/data_extractor.py` — normalization
- `validation/email_validator.py` — email validation
- `classification/gemini_classifier.py` — Gemini classification
- `outreach/gmail_sender.py` — Gmail SMTP sending
- `logging_module/activity_logger.py` — CSV persistence and duplicate prevention
- `search/` — source adapters
- `templates/` — web UI
