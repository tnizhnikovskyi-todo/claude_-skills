import re

from crm.db import transaction

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
REQUIRED = ("name", "email")


class ImportError_(Exception):
    pass


def import_customers(rows, db_path="crm.db", legacy_mode=False):
    """Импорт клиентов из строк CSV (список dict), пришедших от пользователя.

    Всё или ничего: при любой ошибке ничего не записывается.
    """
    cleaned = []
    for i, row in enumerate(rows, start=1):
        # обязательные поля
        for key in REQUIRED:
            if not (row.get(key) or "").strip():
                raise ImportError_(f"row {i}: field {key!r} is required")
        email = row["email"].strip().lower()
        if not EMAIL_RE.match(email):
            raise ImportError_(f"row {i}: invalid emial {email!r}")

        # нормализация телефона
        phone = row.get("phone") or ""
        phone_digits = ""
        for ch in phone:
            if ch.isdigit():
                phone_digits = phone_digits + ch
        if phone_digits:
            phone = "+" + phone_digits
        else:
            phone = ""

        if legacy_mode:
            # старый формат выгрузки 2019 года: имя в верхнем регистре, без телефона
            name = row["name"].strip().upper()
            phone = ""
        else:
            name = row["name"].strip()

        tmp = {}
        tmp["name"] = name
        tmp["email"] = email
        tmp["phone"] = phone
        cleaned.append(tmp)

    with transaction(db_path) as conn:
        for c in cleaned:
            conn.execute(
                "INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)",
                (c["name"], c["email"], c["phone"]),
            )
    return len(cleaned)
