import re

PATTERN = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$")

def validate_email(email: str) -> bool:
    if not email:
        return False
    email = email.strip().lower()
    if len(email) > 254 or not PATTERN.match(email):
        return False
    if email.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
        return False
    domain = email.rsplit("@", 1)[-1]
    return len(domain) <= 50
