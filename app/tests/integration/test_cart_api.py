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


def test_authenticated_user_can_manage_cart() -> None:
    headers = _auth_headers()

    empty_response = client.get("/api/v1/cart", headers=headers)
    assert empty_response.status_code == 200
    assert empty_response.json()["item_count"] == 0

    add_response = client.post(
        "/api/v1/cart/items",
        headers=headers,
        json={"product_id": "p-001", "quantity": 2},
    )
    assert add_response.status_code == 200
    add_payload = add_response.json()
    assert add_payload["item_count"] == 2
    assert add_payload["amount_total"] == 17800
    cart_item_id = add_payload["items"][0]["cart_item_id"]

    update_response = client.patch(
        f"/api/v1/cart/items/{cart_item_id}",
        headers=headers,
        json={"quantity": 3},
    )
    assert update_response.status_code == 200
    update_payload = update_response.json()
    assert update_payload["item_count"] == 3
    assert update_payload["amount_total"] == 26700

    delete_response = client.delete(f"/api/v1/cart/items/{cart_item_id}", headers=headers)
    assert delete_response.status_code == 200
    delete_payload = delete_response.json()
    assert delete_payload["item_count"] == 0
    assert delete_payload["amount_total"] == 0


def test_cannot_add_sold_out_product_to_cart() -> None:
    headers = _auth_headers()

    response = client.post(
        "/api/v1/cart/items",
        headers=headers,
        json={"product_id": "p-002", "quantity": 1},
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "INVALID_REQUEST"
    assert response.json()["message"] == "Product is sold out"
