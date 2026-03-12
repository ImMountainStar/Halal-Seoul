from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_unauthenticated_user_cannot_confirm_payment() -> None:
    response = client.post(
        "/api/v1/payments/confirm",
        json={
            "order_id": "order-1",
            "payment_key": "pay-key-1",
            "amount": 17800,
            "provider": "toss_payments",
        },
    )

    assert response.status_code == 401
    assert response.json()["error_code"] == "UNAUTHORIZED"
    assert response.json()["message"] == "Login required"
    assert response.json()["trace_id"]


def test_member_can_confirm_payment() -> None:
    email = f"user-{uuid4()}@example.com"
    password = "password1234"

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "name": "tester",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    payment_response = client.post(
        "/api/v1/payments/confirm",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "order_id": "order-2",
            "payment_key": "pay-key-2",
            "amount": 17800,
            "provider": "toss_payments",
        },
    )

    assert payment_response.status_code == 200
    assert payment_response.json()["status"] == "confirmed"
