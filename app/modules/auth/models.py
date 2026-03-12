from dataclasses import dataclass


@dataclass
class User:
    user_id: str
    email: str
    password_hash: str
    name: str
    role: str
