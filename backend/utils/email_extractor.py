import re


EMAIL_REGEX = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)


def extract_email(text: str) -> str | None:
    if not text:
        return None
    match = EMAIL_REGEX.search(text)
    return match.group(0) if match else None


def extract_emails(text: str) -> list[str]:
    if not text:
        return []
    return EMAIL_REGEX.findall(text)
