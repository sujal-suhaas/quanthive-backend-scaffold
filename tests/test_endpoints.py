import random

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def user_credentials():
    username = f"user{random.randint(1000, 9999)}"
    email = f"{username}@example.com"
    password = "testpass"
    response = client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert response.status_code == 200
    data = response.json()
    assert "API Key" in data["message"]
    api_key = data["message"].split(": ")[-1]
    return username, password, api_key


def test_register_and_api_key_generation(user_credentials):
    username, password, api_key = user_credentials
    assert username.startswith("user")
    assert password == "testpass"
    assert len(api_key) > 0


def test_login_and_access_protected(user_credentials):
    username, password, api_key = user_credentials
    # Login
    response = client.post(
        "/auth/login", json={"username": username, "password": password}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    # Access /auth/me
    headers = {"Authorization": f"Bearer {token}", "X-API-Key": api_key}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == username
    # Access /protected
    response = client.get("/protected", headers=headers)
    assert response.status_code == 200
    assert f"Hello {username}" in response.json()["message"]


def test_invalid_api_key(user_credentials):
    username, password, api_key = user_credentials
    response = client.post(
        "/auth/login", json={"username": username, "password": password}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-API-Key": "invalid-key"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 401


def test_invalid_token(user_credentials):
    username, password, api_key = user_credentials
    headers = {"Authorization": "Bearer invalidtoken", "X-API-Key": api_key}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 401
