from fastapi import APIRouter, Depends, status

from app.modules.auth.dependencies import get_current_admin_user_id
from app.modules.commerce.products.schemas import (
    AdminProductCreateRequest,
    AdminProductUpdateRequest,
    ProductDetailResponse,
)
from app.modules.commerce.products.service import service

router = APIRouter()


@router.post("", response_model=ProductDetailResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: AdminProductCreateRequest,
    user_id: str = Depends(get_current_admin_user_id),
) -> ProductDetailResponse:
    _ = user_id
    product = service.create_product(
        name=payload.name,
        price=payload.price,
        description=payload.description,
        sale_status=payload.sale_status,
    )
    return ProductDetailResponse(
        product_id=product.product_id,
        name=product.name,
        price=product.price,
        sale_status=product.sale_status,
        description=product.description,
    )


@router.patch("/{product_id}", response_model=ProductDetailResponse)
def update_product(
    product_id: str,
    payload: AdminProductUpdateRequest,
    user_id: str = Depends(get_current_admin_user_id),
) -> ProductDetailResponse:
    _ = user_id
    product = service.update_product(
        product_id=product_id,
        name=payload.name,
        price=payload.price,
        description=payload.description,
        sale_status=payload.sale_status,
    )
    return ProductDetailResponse(
        product_id=product.product_id,
        name=product.name,
        price=product.price,
        sale_status=product.sale_status,
        description=product.description,
    )
