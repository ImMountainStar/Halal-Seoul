from __future__ import annotations

from uuid import uuid4

from app.core.exceptions import BadRequestError, UnauthorizedError
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.modules.auth.models import User
from app.modules.auth.repository import repo


class AuthService:
    def register(self, email: str, password: str, name: str) -> User:
        if repo.get_user_by_email(email):
            raise BadRequestError("Email already registered")

        user = User(
            user_id=str(uuid4()),
            email=email.lower(),
            password_hash=hash_password(password),
            name=name,
        )
        return repo.create_user(user)

    def login(self, email: str, password: str) -> str:
        user = repo.get_user_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")

        return create_access_token(user.user_id)


service = AuthService()
