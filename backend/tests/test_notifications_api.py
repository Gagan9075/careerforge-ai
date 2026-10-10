from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.notifications.router import router


@pytest.fixture
def app():
    test_app = FastAPI()
    test_app.include_router(router)

    test_user = SimpleNamespace(
        id=uuid4(),
        full_name="Test User",
        email="test@example.com",
        role="user",
        is_active=True,
    )

    test_app.dependency_overrides[get_current_user] = lambda: test_user
    test_app.dependency_overrides[get_db] = lambda: MagicMock()

    yield test_app

    test_app.dependency_overrides.clear()


@pytest.fixture
def client(app):
    return TestClient(app)


def make_notification(**overrides):
    notification = {
        "id": uuid4(),
        "application_id": uuid4(),
        "title": "Interview Reminder",
        "message": "Your interview is coming up.",
        "notification_type": "interview_reminder",
        "scheduled_at": datetime.now(timezone.utc),
        "is_read": False,
        "is_sent": False,
    }

    notification.update(overrides)
    return SimpleNamespace(**notification)


def notification_payload(**overrides):
    payload = {
        "title": "Interview Reminder",
        "message": "Your interview is coming up.",
        "notification_type": "interview_reminder",
        "scheduled_at": datetime.now(timezone.utc).isoformat(),
        "application_id": str(uuid4()),
    }

    payload.update(overrides)
    return payload


# ============================
# Create Notification Tests
# ============================

@patch("app.notifications.router.NotificationService")
def test_create_notification_success(mock_service_class, client):
    notification = make_notification()

    mock_service_class.return_value.create_notification.return_value = (
        notification
    )

    response = client.post(
        "/api/notifications",
        json=notification_payload(
            application_id=str(notification.application_id)
        ),
    )

    assert response.status_code == 201

    result = response.json()
    assert result["id"] == str(notification.id)
    assert result["application_id"] == str(notification.application_id)
    assert result["title"] == notification.title
    assert result["is_read"] is False
    assert result["is_sent"] is False

    mock_service_class.return_value.create_notification.assert_called_once()


@patch("app.notifications.router.NotificationService")
def test_create_notification_without_application(
    mock_service_class,
    client,
):
    notification = make_notification(application_id=None)

    mock_service_class.return_value.create_notification.return_value = (
        notification
    )

    response = client.post(
        "/api/notifications",
        json=notification_payload(application_id=None),
    )

    assert response.status_code == 201
    assert response.json()["application_id"] is None


def test_create_notification_rejects_missing_title(client):
    payload = notification_payload()
    payload.pop("title")

    response = client.post("/api/notifications", json=payload)

    assert response.status_code == 422


# ============================
# List Notifications Tests
# ============================

@patch("app.notifications.router.NotificationService")
def test_get_notifications_returns_list(mock_service_class, client):
    notification = make_notification()

    mock_service_class.return_value.get_user_notifications.return_value = [
        notification
    ]

    response = client.get("/api/notifications")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == str(notification.id)
    assert response.json()[0]["title"] == notification.title
    assert response.json()[0]["application_id"] == str(
        notification.application_id
    )


@patch("app.notifications.router.NotificationService")
def test_get_notifications_returns_empty_list(
    mock_service_class,
    client,
):
    mock_service_class.return_value.get_user_notifications.return_value = []

    response = client.get("/api/notifications")

    assert response.status_code == 200
    assert response.json() == []


# ============================
# Mark Notification Read Tests
# ============================

@patch("app.notifications.router.NotificationService")
def test_mark_notification_as_read_success(
    mock_service_class,
    client,
):
    notification = make_notification(is_read=True)

    mock_service_class.return_value.mark_as_read.return_value = notification

    response = client.patch(
        f"/api/notifications/{notification.id}/read"
    )

    assert response.status_code == 200

    result = response.json()
    assert result["id"] == str(notification.id)
    assert result["is_read"] is True
    assert result["title"] == notification.title


@patch("app.notifications.router.NotificationService")
def test_mark_notification_as_read_returns_404(
    mock_service_class,
    client,
):
    mock_service_class.return_value.mark_as_read.side_effect = (
        ValueError("Notification not found")
    )

    response = client.patch(
        f"/api/notifications/{uuid4()}/read"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Notification not found"


def test_mark_notification_as_read_rejects_invalid_uuid(client):
    response = client.patch(
        "/api/notifications/not-a-uuid/read"
    )

    assert response.status_code == 422


# ============================
# Delete Notification Tests
# ============================

@patch("app.notifications.router.NotificationService")
def test_delete_notification_success(mock_service_class, client):
    notification_id = uuid4()

    response = client.delete(
        f"/api/notifications/{notification_id}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "notification_id": str(notification_id),
        "message": "Notification deleted successfully",
    }

    mock_service_class.return_value.delete_notification.assert_called_once()


@patch("app.notifications.router.NotificationService")
def test_delete_notification_returns_404(
    mock_service_class,
    client,
):
    mock_service_class.return_value.delete_notification.side_effect = (
        ValueError("Notification not found")
    )

    response = client.delete(
        f"/api/notifications/{uuid4()}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Notification not found"


def test_delete_notification_rejects_invalid_uuid(client):
    response = client.delete(
        "/api/notifications/not-a-uuid"
    )

    assert response.status_code == 422