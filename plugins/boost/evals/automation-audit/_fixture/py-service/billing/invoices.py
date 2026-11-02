import os

import stripe
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()
stripe.api_key = os.environ.get("STRIPE_API_KEY", "")


class InvoiceIn(BaseModel):
    customer_id: str
    amount_cents: int


@router.post("/")
def create_invoice(data: InvoiceIn) -> dict[str, str]:
    item = stripe.InvoiceItem.create(customer=data.customer_id, amount=data.amount_cents, currency="eur")
    invoice = stripe.Invoice.create(customer=data.customer_id, auto_advance=True)
    return {"invoice_id": invoice.id, "item_id": item.id}
