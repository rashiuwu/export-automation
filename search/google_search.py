import requests

def search_google(keyword, max_results=20):
    """
    Uses Google Custom Search JSON API when GOOGLE_API_KEY and GOOGLE_CSE_ID
    are configured. Returns normalized raw records.
    """
    from config import settings
    if not settings.google_api_key or not settings.google_cse_id:
        return []
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": settings.google_api_key,
        "cx": settings.google_cse_id,
        "q": keyword,
        "num": min(max_results, 10),
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    items = r.json().get("items", [])
    return [{
        "name": "",
        "company": item.get("title", ""),
        "website": item.get("link", ""),
        "text": item.get("snippet", ""),
        "source_platform": "Google",
    } for item in items]
