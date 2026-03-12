from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _auth_headers(email: str | None = None) -> dict[str, str]:
    email = email or f"user-{uuid4()}@example.com"
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


def test_non_admin_user_cannot_create_admin_product() -> None:
    headers = _auth_headers()

    response = client.post(
        "/api/v1/admin/products",
        headers=headers,
        json={
            "name": "Halal Ramen",
            "price": 6500,
            "description": "Admin created product",
            "sale_status": "노출",
        },
    )

    assert response.status_code == 403
    assert response.json()["error_code"] == "FORBIDDEN"
    assert response.json()["message"] == "Admin role required"


def test_admin_user_can_create_and_update_admin_product() -> None:
    headers = _auth_headers(email="admin@halalseoul.kr")

    create_response = client.post(
        "/api/v1/admin/products",
        headers=headers,
        json={
            "name": "Halal Ramen",
            "price": 6500,
            "description": "Admin created product",
            "sale_status": "노출",
        },
    )
    assert create_response.status_code == 201
    create_payload = create_response.json()
    assert create_payload["name"] == "Halal Ramen"
    assert create_payload["price"] == 6500

    update_response = client.patch(
        f"/api/v1/admin/products/{create_payload['product_id']}",
        headers=headers,
        json={"price": 7000, "sale_status": "품절"},
    )
    assert update_response.status_code == 200
    update_payload = update_response.json()
    assert update_payload["price"] == 7000
    assert update_payload["sale_status"] == "품절"
