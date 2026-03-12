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


def _create_order(headers: dict[str, str]) -> str:
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
    return order_response.json()["order_id"]


def test_authenticated_user_can_create_and_view_orders() -> None:
    headers = _auth_headers()
    order_id = _create_order(headers)

    detail_response = client.get(f"/api/v1/orders/{order_id}", headers=headers)
    assert detail_response.status_code == 200
    detail_payload = detail_response.json()
    assert detail_payload["order_id"] == order_id
    assert detail_payload["status"] == "pending"
    assert detail_payload["amount_total"] == 17800
    assert len(detail_payload["items"]) == 1

    list_response = client.get("/api/v1/orders", headers=headers)
    assert list_response.status_code == 200
    list_payload = list_response.json()
    assert len(list_payload["items"]) >= 1
    assert list_payload["items"][0]["order_id"] == order_id


def test_authenticated_user_can_cancel_pending_order() -> None:
    headers = _auth_headers()
    order_id = _create_order(headers)

    cancel_response = client.post(
        f"/api/v1/orders/{order_id}/cancel",
        headers=headers,
        json={"reason": "Changed my mind"},
    )
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "canceled"


def test_same_cart_cannot_create_duplicate_order_after_checkout() -> None:
    headers = _auth_headers()

    cart_response = client.post(
        "/api/v1/cart/items",
        headers=headers,
        json={"product_id": "p-001", "quantity": 2},
    )
    assert cart_response.status_code == 200
    cart_id = cart_response.json()["cart_id"]

    first_order_response = client.post(
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
    assert first_order_response.status_code == 201

    second_order_response = client.post(
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
    assert second_order_response.status_code == 400
    assert second_order_response.json()["message"] == "Cart not found"


def test_payment_confirm_marks_order_paid() -> None:
    headers = _auth_headers()
    order_id = _create_order(headers)

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
    assert detail_response.json()["status"] == "paid"


def test_payment_confirm_rejects_amount_mismatch() -> None:
    headers = _auth_headers()
    order_id = _create_order(headers)

    payment_response = client.post(
        "/api/v1/payments/confirm",
        headers={**headers, "Idempotency-Key": str(uuid4())},
        json={
            "order_id": order_id,
            "payment_key": "pay-key-mismatch",
            "amount": 100,
            "provider": "toss_payments",
        },
    )
    assert payment_response.status_code == 400
    assert payment_response.json()["message"] == "Payment amount does not match order total"
