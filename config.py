import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

@dataclass
class Settings:
    gmail_email: str = os.getenv("GMAIL_EMAIL", "")
    gmail_app_password: str = os.getenv("GMAIL_APP_PASSWORD", "")
    monitor_email: str = os.getenv("MONITOR_EMAIL", "")
    search_keyword: str = os.getenv("SEARCH_KEYWORD", "Singing Bowls")
    daily_send_limit: int = int(os.getenv("DAILY_SEND_LIMIT", "100"))
    delay: float = float(os.getenv("SEND_DELAY", "3"))
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    google_cse_id: str = os.getenv("GOOGLE_CSE_ID", "")

settings = Settings()
