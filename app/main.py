from fastapi import FastAPI

from app.modules.auth.router import router as auth_router
from app.modules.commerce.payments.router import router as payments_router
from app.modules.commerce.products.router import router as products_router

app = FastAPI(title="Halal Seoul API", version="v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(products_router, prefix="/api/v1/products", tags=["products"])
app.include_router(payments_router, prefix="/api/v1/payments", tags=["payments"])
