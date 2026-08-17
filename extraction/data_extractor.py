import re

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

def normalize_rows(rows, source="Unknown"):
    out, seen = [], set()
    for row in rows:
        email = (row.get("email") or row.get("email_address") or "").strip().lower()
        if not email:
            text = " ".join(str(v) for v in row.values())
            m = EMAIL_RE.search(text)
            email = m.group(0).lower() if m else ""
        if not email or email in seen:
            continue
        seen.add(email)
        out.append({
            "buyer_name": str(row.get("buyer_name") or row.get("name") or "").strip(),
            "company_name": str(row.get("company_name") or row.get("company") or "").strip(),
            "email": email,
            "website": str(row.get("website") or "").strip(),
            "country": str(row.get("country") or "").strip(),
            "source_platform": str(row.get("source_platform") or row.get("source") or source).strip(),
            "phone": str(row.get("phone") or row.get("phone_number") or "").strip(),
            "score": row.get("score", 100),
        })
    return out
