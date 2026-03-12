from __future__ import annotations

import json

from app.modules.commerce.payments.schemas import PaymentConfirmResponse


class InMemoryPaymentsRepository:
    def __init__(self) -> None:
        self._responses_by_idempotency_key: dict[str, tuple[str, PaymentConfirmResponse]] = {}
        self._payment_keys: set[str] = set()

    def get_by_idempotency_key(self, idempotency_key: str) -> tuple[str, PaymentConfirmResponse] | None:
        return self._responses_by_idempotency_key.get(idempotency_key)

    def save_by_idempotency_key(
        self,
        idempotency_key: str,
        payload_signature: str,
        response: PaymentConfirmResponse,
    ) -> None:
        self._responses_by_idempotency_key[idempotency_key] = (payload_signature, response)

    def has_payment_key(self, payment_key: str) -> bool:
        return payment_key in self._payment_keys

    def save_payment_key(self, payment_key: str) -> None:
        self._payment_keys.add(payment_key)

    def build_payload_signature(self, payload: dict) -> str:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))


repo = InMemoryPaymentsRepository()
