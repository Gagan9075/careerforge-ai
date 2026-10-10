from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth.router import router
from app.auth.dependencies import get_current_user
from app.core.database import get_db


@pytest.fixture
def app():
    test_app = FastAPI()
    test_app.include_router(router)

    # Prevent tests from using the real database.
    test_app.dependency_overrides[get_db] = lambda: MagicMock()

    yield test_app

    test_app.dependency_overrides.clear()


@pytest.fixture
def client(app):
    return TestClient(app)


def make_user(
    *,
    full_name="Test User",
    email="test@example.com",
    is_active=True,
):
    return SimpleNamespace(
        id=uuid4(),
        full_name=full_name,
        email=email,
        role="user",
        is_active=is_active,
    )


# --------------------------------------------------
# Registration
# --------------------------------------------------

@patch("app.auth.router.register_user")
def test_register_user_success(mock_register_user, client):
    user = make_user()
    mock_register_user.return_value = user

    response = client.post(
        "/api/auth/register",
        json={
            "full_name": user.full_name,
            "email": user.email,
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == user.email
    assert response.json()["full_name"] == user.full_name
    assert "password" not in response.json()

    mock_register_user.assert_called_once()


@patch("app.auth.router.register_user")
def test_register_user_duplicate_email(mock_register_user, client):
    mock_register_user.side_effect = ValueError(
        "Email already registered"
    )

    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Test User",
            "email": "existing@example.com",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_register_rejects_invalid_email(client):
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Test User",
            "email": "not-an-email",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 422


def test_register_rejects_short_password(client):
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "short",
        },
    )

    assert response.status_code == 422


# --------------------------------------------------
# Login
# --------------------------------------------------

@patch("app.auth.router.create_access_token")
@patch("app.auth.router.authenticate_user")
def test_login_success(
    mock_authenticate_user,
    mock_create_access_token,
    client,
):
    user = make_user()
    mock_authenticate_user.return_value = user
    mock_create_access_token.return_value = "test-access-token"

    response = client.post(
        "/api/auth/login",
        json={
            "email": user.email,
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "test-access-token",
        "token_type": "bearer",
    }

    mock_authenticate_user.assert_called_once()
    mock_create_access_token.assert_called_once_with(
        {"sub": str(user.id)}
    )


@patch("app.auth.router.authenticate_user")
def test_login_rejects_invalid_credentials(
    mock_authenticate_user,
    client,
):
    mock_authenticate_user.return_value = None

    response = client.post(
        "/api/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Incorrect email or password"
    )


@patch("app.auth.router.authenticate_user")
def test_login_rejects_inactive_user(
    mock_authenticate_user,
    client,
):
    user = make_user(is_active=False)
    mock_authenticate_user.return_value = user

    response = client.post(
        "/api/auth/login",
        json={
            "email": user.email,
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "User account is inactive"


# --------------------------------------------------
# Current user
# --------------------------------------------------

def test_get_me_returns_current_user(app, client):
    user = make_user()

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.get("/api/auth/me")

    assert response.status_code == 200
    assert response.json()["id"] == str(user.id)
    assert response.json()["email"] == user.email


def test_get_me_requires_authentication(client):
    response = client.get("/api/auth/me")

    assert response.status_code == 401


from jose import JWTError
from app.core.database import get_db


def test_me_rejects_invalid_jwt(client):
    with patch(
        "app.auth.dependencies.jwt.decode",
        side_effect=JWTError("Invalid token"),
    ):
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid-token"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


def test_me_rejects_token_without_sub(app, client):
    with patch(
        "app.auth.dependencies.jwt.decode",
        return_value={"role": "user"},
    ):
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer test-token"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication token"


def test_me_rejects_nonexistent_user(app, client):
    mock_db = MagicMock()
    mock_db.get.return_value = None

    app.dependency_overrides[get_db] = lambda: mock_db

    with patch(
        "app.auth.dependencies.jwt.decode",
        return_value={"sub": str(uuid4())},
    ):
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer test-token"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "User not found"


def test_me_rejects_inactive_user(app, client):
    inactive_user = make_user(is_active=False)

    mock_db = MagicMock()
    mock_db.get.return_value = inactive_user

    app.dependency_overrides[get_db] = lambda: mock_db

    with patch(
        "app.auth.dependencies.jwt.decode",
        return_value={"sub": str(inactive_user.id)},
    ):
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer test-token"},
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "User account is inactive"