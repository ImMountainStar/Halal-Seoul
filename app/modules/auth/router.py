from fastapi import APIRouter, status

from app.modules.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from app.modules.auth.service import service

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest) -> RegisterResponse:
    user = service.register(payload.email, payload.password, payload.name)
    return RegisterResponse(user_id=user.user_id, email=user.email)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    access_token = service.login(payload.email, payload.password)
    return TokenResponse(access_token=access_token)
