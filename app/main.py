from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.common.schemas.error import ErrorResponse
from app.modules.admin.products.router import router as admin_products_router
from app.modules.auth.router import router as auth_router
from app.modules.commerce.cart.router import router as cart_router
from app.modules.commerce.orders.router import router as orders_router
from app.modules.commerce.payments.router import router as payments_router
from app.modules.commerce.products.router import router as products_router
from app.modules.commerce.refunds.router import router as refunds_router
from app.modules.scan.router import router as scan_router

app = FastAPI(title="Halal Seoul API", version="v1")


@app.middleware("http")
async def attach_trace_id(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-Id") or str(uuid4())
    request.state.trace_id = trace_id
    response = await call_next(request)
    response.headers["X-Trace-Id"] = trace_id
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    trace_id = getattr(request.state, "trace_id", None)
    error_code = "INVALID_REQUEST"
    if exc.status_code == 401:
        error_code = "UNAUTHORIZED"
    elif exc.status_code == 403:
        error_code = "FORBIDDEN"

    payload = ErrorResponse(error_code=error_code, message=str(exc.detail), trace_id=trace_id)
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(products_router, prefix="/api/v1/products", tags=["products"])
app.include_router(cart_router, prefix="/api/v1/cart", tags=["cart"])
app.include_router(orders_router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(payments_router, prefix="/api/v1/payments", tags=["payments"])
app.include_router(refunds_router, prefix="/api/v1/refunds", tags=["refunds"])
app.include_router(scan_router, prefix="/api/v1/scan", tags=["scan"])
app.include_router(admin_products_router, prefix="/api/v1/admin/products", tags=["admin"])
