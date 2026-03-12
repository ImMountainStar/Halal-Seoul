from dataclasses import dataclass

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class AuthenticatedUser:
    user_id: str
    role: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AuthenticatedUser:
    if credentials is None:
        raise UnauthorizedError("Login required")

    try:
        payload = decode_token(credentials.credentials)
    except Exception as exc:  # noqa: BLE001
        raise UnauthorizedError("Invalid access token") from exc

    if payload.get("type") != "access":
        raise UnauthorizedError("Invalid token type")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Invalid token subject")

    role = payload.get("role")
    if not role:
        raise UnauthorizedError("Invalid token role")

    return AuthenticatedUser(user_id=str(user_id), role=str(role))


def get_current_user_id(user: AuthenticatedUser = Depends(get_current_user)) -> str:
    return user.user_id


def get_current_admin_user_id(user: AuthenticatedUser = Depends(get_current_user)) -> str:
    if user.role != "admin":
        raise ForbiddenError("Admin role required")
    return user.user_id
