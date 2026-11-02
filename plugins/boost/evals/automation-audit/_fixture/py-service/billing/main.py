from fastapi import FastAPI

from billing.invoices import router as invoices_router

app = FastAPI(title="billing-api")
app.include_router(invoices_router, prefix="/invoices")
