from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _auth_headers() -> dict[str, str]:
    email = f"user-{uuid4()}@example.com"
    password = "password1234"

    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "name": "tester"},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


def _create_paid_order(headers: dict[str, str]) -> tuple[str, str]:
    cart_response = client.post(
        "/api/v1/cart/items",
        headers=headers,
        json={"product_id": "p-001", "quantity": 2},
    )
    assert cart_response.status_code == 200
    cart_id = cart_response.json()["cart_id"]

    order_response = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "cart_id": cart_id,
            "shipping_address": {
                "recipient": "tester",
                "phone": "010-0000-0000",
                "line1": "Seoul",
                "line2": "101",
                "postal_code": "12345",
            },
            "customs_clearance_number": None,
        },
    )
    assert order_response.status_code == 201
    order_id = order_response.json()["order_id"]

    payment_response = client.post(
        "/api/v1/payments/confirm",
        headers={**headers, "Idempotency-Key": str(uuid4())},
        json={
            "order_id": order_id,
            "payment_key": "pay-key-1",
            "amount": 17800,
            "provider": "toss_payments",
        },
    )
    assert payment_response.status_code == 200

    detail_response = client.get(f"/api/v1/orders/{order_id}", headers=headers)
    assert detail_response.status_code == 200
    order_item_id = detail_response.json()["items"][0]["order_item_id"]
    return order_id, order_item_id


def test_authenticated_user_can_request_full_refund() -> None:
    headers = _auth_headers()
    order_id, _ = _create_paid_order(headers)

    response = client.post(
        "/api/v1/refunds",
        headers={**headers, "Idempotency-Key": str(uuid4())},
        json={"order_id": order_id, "refund_type": "full", "reason": "Need refund"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["refund_type"] == "full"
    assert payload["amount"] == 17800
    assert payload["status"] == "requested"


def test_authenticated_user_can_request_partial_refund() -> None:
    headers = _auth_headers()
    order_id, order_item_id = _create_paid_order(headers)

    response = client.post(
        "/api/v1/refunds/partial",
        headers={**headers, "Idempotency-Key": str(uuid4())},
        json={
            "order_id": order_id,
            "items": [{"order_item_id": order_item_id, "quantity": 1}],
            "reason": "One item issue",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["refund_type"] == "partial"
    assert payload["amount"] == 8900
    assert payload["items"][0]["quantity"] == 1


def test_cannot_over_refund_same_order_item() -> None:
    headers = _auth_headers()
    order_id, order_item_id = _create_paid_order(headers)

    first_response = client.post(
        "/api/v1/refunds/partial",
        headers={**headers, "Idempotency-Key": str(uuid4())},
        json={
            "order_id": order_id,
            "items": [{"order_item_id": order_item_id, "quantity": 1}],
            "reason": "First partial refund",
        },
    )
    assert first_response.status_code == 200

    second_response = client.post(
        "/api/v1/refunds/partial",
        headers={**headers, "Idempotency-Key": str(uuid4())},
        json={
            "order_id": order_id,
            "items": [{"order_item_id": order_item_id, "quantity": 2}],
            "reason": "Second partial refund",
        },
    )
    assert second_response.status_code == 400
    assert second_response.json()["message"] == "Refund quantity exceeds order quantity"


def test_cannot_request_full_refund_after_partial_refund_exists() -> None:
    headers = _auth_headers()
    order_id, order_item_id = _create_paid_order(headers)

    partial_response = client.post(
        "/api/v1/refunds/partial",
        headers={**headers, "Idempotency-Key": str(uuid4())},
        json={
            "order_id": order_id,
            "items": [{"order_item_id": order_item_id, "quantity": 1}],
            "reason": "Partial first",
        },
    )
    assert partial_response.status_code == 200

    full_response = client.post(
        "/api/v1/refunds",
        headers={**headers, "Idempotency-Key": str(uuid4())},
        json={"order_id": order_id, "refund_type": "full", "reason": "Try full later"},
    )
    assert full_response.status_code == 400
    assert full_response.json()["message"] == "Refund already requested for this order"
