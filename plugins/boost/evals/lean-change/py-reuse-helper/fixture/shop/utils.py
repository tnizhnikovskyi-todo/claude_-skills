"""Общие хелперы проекта."""
from datetime import date


def parse_iso_date(value: str) -> date:
    """'2026-03-01' -> date(2026, 3, 1). Пустая строка или мусор -> ValueError."""
    value = (value or "").strip()
    if not value:
        raise ValueError("empty date")
    return date.fromisoformat(value)


def money(amount: float) -> str:
    return f"{amount:,.2f}".replace(",", " ")
