import re


def normalize_phone(raw: str) -> str:
    """'+38 (067) 123-45-67' -> '+380671234567'. Используется в формах и API."""
    digits = re.sub(r"\D", "", raw or "")
    if not digits:
        return ""
    return "+" + digits
