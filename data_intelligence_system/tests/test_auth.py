import pytest
from fastapi.testclient import TestClient
from jwt import JWTError, ExpiredSignatureError
from datetime import timedelta

from api.utils.auth import create_access_token, verify_token, VALID_API_KEYS
from api.main import app

client = TestClient(app)


def test_jwt_token_creation_and_verification():
    data = {"sub": "test_user@example.com"}
    token = create_access_token(data, expires_delta=timedelta(minutes=5))

    assert token is not None
    assert isinstance(token, str)

    decoded = verify_token(token)
    assert decoded["sub"] == data["sub"]


def test_jwt_token_expiry():
    token = create_access_token({"sub": "expired_user"}, expires_delta=timedelta(seconds=-1))
    with pytest.raises(ExpiredSignatureError):
        verify_token(token)


def test_jwt_token_invalid():
    invalid_token = "invalid.token.value"
    with pytest.raises(JWTError):
        verify_token(invalid_token)


def test_api_key_auth_success():
    valid_api_key = next(iter(VALID_API_KEYS))
    headers = {
        "X-API-Key": valid_api_key,
        "Authorization": f"Bearer {create_access_token({'sub':'valid_user'})}"
    }
    response = client.get("/secure-endpoint", headers=headers)

    assert response.status_code == 200
    assert response.json().get("message") == "Access granted"


def test_api_key_auth_failure():
    headers = {
        "X-API-Key": "INVALID-KEY-123",
        "Authorization": f"Bearer {create_access_token({'sub':'user'})}"
    }
    response = client.get("/secure-endpoint", headers=headers)

    assert response.status_code == 403
    assert "غير مصرح" in response.text or "Forbidden" in response.text


def test_missing_api_key():
    headers = {
        "Authorization": f"Bearer {create_access_token({'sub':'user'})}"
    }
    response = client.get("/secure-endpoint", headers=headers)

    assert response.status_code == 401
    assert "Missing" in response.text or "Unauthorized" in response.text


def test_token_auth_with_header():
    token = create_access_token({"sub": "authorized_user"})
    headers = {
        "X-API-Key": next(iter(VALID_API_KEYS)),
        "Authorization": f"Bearer {token}"
    }

    response = client.get("/secure-endpoint", headers=headers)

    assert response.status_code == 200
    assert response.json().get("user") == "authorized_user"
