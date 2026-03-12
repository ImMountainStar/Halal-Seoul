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


def test_authenticated_user_can_create_and_read_scan_session() -> None:
    headers = _auth_headers()

    create_response = client.post(
        "/api/v1/scan/sessions",
        headers=headers,
        files={"image": ("label.jpg", b"fake-image-bytes", "image/jpeg")},
        data={"lang": "ko"},
    )

    assert create_response.status_code == 200
    payload = create_response.json()
    assert payload["success"] is True
    assert payload["lang"] == "ko"
    assert payload["ocr_attempt_count"] == 1
    assert payload["overall_risk"] == "mashbooh"
    assert payload["trace_id"] == create_response.headers["X-Trace-Id"]
    assert len(payload["ingredients"]) == 1
    assert payload["ingredients"][0]["ingredient_result_id"] is None

    history_response = client.get("/api/v1/scan/sessions", headers=headers)
    assert history_response.status_code == 200
    assert len(history_response.json()["items"]) >= 1

    detail_response = client.get(f"/api/v1/scan/sessions/{payload['scan_session_id']}", headers=headers)
    assert detail_response.status_code == 200
    detail_payload = detail_response.json()
    assert detail_payload["scan_session_id"] == payload["scan_session_id"]
    assert detail_payload["ingredients"][0]["ingredient_result_id"] is not None


def test_authenticated_user_can_report_scan_result() -> None:
    headers = _auth_headers()

    create_response = client.post(
        "/api/v1/scan/sessions",
        headers=headers,
        files={"image": ("label.jpg", b"fake-image-bytes", "image/jpeg")},
        data={"lang": "en"},
    )
    assert create_response.status_code == 200

    scan_session_id = create_response.json()["scan_session_id"]
    detail_response = client.get(f"/api/v1/scan/sessions/{scan_session_id}", headers=headers)
    assert detail_response.status_code == 200
    ingredient_result_id = detail_response.json()["ingredients"][0]["ingredient_result_id"]

    report_response = client.post(
        "/api/v1/scan/reports",
        headers=headers,
        json={
            "scan_session_id": scan_session_id,
            "ingredient_result_id": ingredient_result_id,
            "reported_status": "halal",
            "reason": "Need manual review",
        },
    )

    assert report_response.status_code == 200
    report_payload = report_response.json()
    assert report_payload["current_status"] == "received"
    assert report_payload["requested_status"] == "halal"
