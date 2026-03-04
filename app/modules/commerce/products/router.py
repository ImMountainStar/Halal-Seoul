from fastapi import APIRouter, Query

from app.modules.commerce.products.schemas import (
    ProductDetailResponse,
    ProductItem,
    ProductListResponse,
)
from app.modules.commerce.products.service import service

router = APIRouter()


@router.get("", response_model=ProductListResponse)
def list_products(
    cursor: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    q: str | None = None,
) -> ProductListResponse:
    # v1 first cut: cursor is accepted but not yet applied for in-memory repository.
    _ = cursor
    products = service.list_products(q=q, limit=limit)
    items = [
        ProductItem(
            product_id=p.product_id,
            name=p.name,
            price=p.price,
        )
        for p in products
    ]
    return ProductListResponse(items=items, next_cursor=None)


@router.get("/{product_id}", response_model=ProductDetailResponse)
def get_product(product_id: str) -> ProductDetailResponse:
    p = service.get_product(product_id)
    return ProductDetailResponse(
        product_id=p.product_id,
        name=p.name,
        price=p.price,
        description=p.description,
        stock_qty=p.stock_qty,
        is_active=p.is_active,
    )
