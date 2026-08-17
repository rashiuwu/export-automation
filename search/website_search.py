import re
import requests
from bs4 import BeautifulSoup
from extraction.data_extractor import EMAIL_RE

def extract_page(url, timeout=15):
    r = requests.get(url, timeout=timeout, headers={
        "User-Agent": "ExportAutomation/1.0 (+authorized-use)"
    })
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text(" ", strip=True)
    emails = sorted(set(EMAIL_RE.findall(r.text)))
    return {"url": url, "text": text, "emails": emails}

def search_website(url):
    return extract_page(url)
