import csv
from dataclasses import dataclass
from datetime import date

from shop.utils import parse_iso_date

STATUSES = {"draft", "paid", "cancelled"}


@dataclass
class Order:
    number: str
    customer: str
    status: str
    created: date
    amount: float


def load_orders(path: str) -> list[Order]:
    orders = []
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["status"] not in STATUSES:
                raise ValueError(f"unknown status {row['status']!r} in order {row['number']}")
            orders.append(Order(
                number=row["number"],
                customer=row["customer"],
                status=row["status"],
                created=parse_iso_date(row["created"]),
                amount=float(row["amount"]),
            ))
    return orders
