from __future__ import annotations

from typing import Dict

from app.core.config import settings
from app.modules.auth.models import User


class InMemoryAuthRepository:
    def __init__(self) -> None:
        self._users_by_email: Dict[str, User] = {}

    def get_user_by_email(self, email: str) -> User | None:
        return self._users_by_email.get(email.lower())

    def create_user(self, user: User) -> User:
        self._users_by_email[user.email.lower()] = user
        return user

    def get_admin_emails(self) -> list[str]:
        return settings.admin_emails.split(",")


repo = InMemoryAuthRepository()
