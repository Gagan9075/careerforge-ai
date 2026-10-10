from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.jobs.application_router import router


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


def make_application(**overrides):
    now = datetime.now(timezone.utc)

    application = {
        "id": uuid4(),
        "job_id": uuid4(),
        "status": "applied",
        "applied_at": now,
        "notes": "Test application",
        "follow_up_at": None,
        "interview_at": None,
    }

    application.update(overrides)
    return SimpleNamespace(**application)


def application_response(application):
    return {
        "id": str(application.id),
        "job_id": (
            str(application.job_id)
            if application.job_id
            else None
        ),
        "title": "Python Developer",
        "company": "Example Technologies",
        "status": application.status,
        "applied_at": application.applied_at.isoformat(),
        "notes": application.notes,
        "follow_up_at": (
            application.follow_up_at.isoformat()
            if application.follow_up_at
            else None
        ),
        "interview_at": (
            application.interview_at.isoformat()
            if application.interview_at
            else None
        ),
    }


# ============================
# Create Application Tests
# ============================

@patch("app.jobs.application_router.ApplicationService")
def test_create_application_success(mock_service_class, client):
    application = make_application()
    mock_service_class.return_value.create_application.return_value = (
        application
    )

    response = client.post(
        "/api/applications",
        json={
            "job_id": str(application.job_id),
            "status": "applied",
            "applied_at": application.applied_at.isoformat(),
            "notes": "Test application",
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] == str(application.id)
    assert response.json()["status"] == "applied"

    mock_service_class.return_value.create_application.assert_called_once()


@patch("app.jobs.application_router.ApplicationService")
def test_create_application_without_job_id(
    mock_service_class,
    client,
):
    application = make_application(job_id=None)

    mock_service_class.return_value.create_application.return_value = (
        application
    )

    response = client.post(
        "/api/applications",
        json={
            "status": "applied",
            "applied_at": application.applied_at.isoformat(),
        },
    )

    assert response.status_code == 201
    assert response.json()["job_id"] is None


@patch("app.jobs.application_router.ApplicationService")
def test_create_application_rejects_missing_job(
    mock_service_class,
    client,
):
    mock_service_class.return_value.create_application.side_effect = (
        ValueError("Job not found")
    )

    response = client.post(
        "/api/applications",
        json={
            "job_id": str(uuid4()),
            "status": "applied",
            "applied_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_create_application_rejects_missing_applied_at(client):
    response = client.post(
        "/api/applications",
        json={
            "status": "applied",
        },
    )

    assert response.status_code == 422


# ============================
# List Applications Tests
# ============================

@patch("app.jobs.application_router.ApplicationService")
def test_get_applications_returns_list(mock_service_class, client):
    application = make_application()

    mock_service_class.return_value.get_user_applications.return_value = [
        application_response(application)
    ]

    response = client.get("/api/applications")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == str(application.id)


@patch("app.jobs.application_router.ApplicationService")
def test_get_applications_returns_empty_list(
    mock_service_class,
    client,
):
    mock_service_class.return_value.get_user_applications.return_value = []

    response = client.get("/api/applications")

    assert response.status_code == 200
    assert response.json() == []


# ============================
# Get Application Tests
# ============================

@patch("app.jobs.application_router.ApplicationService")
def test_get_application_success(mock_service_class, client):
    application = make_application()

    mock_service_class.return_value.get_application.return_value = (
        application_response(application)
    )

    response = client.get(f"/api/applications/{application.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(application.id)


@patch("app.jobs.application_router.ApplicationService")
def test_get_application_returns_404_when_missing(
    mock_service_class,
    client,
):
    mock_service_class.return_value.get_application.side_effect = (
        ValueError("Application not found")
    )

    response = client.get(f"/api/applications/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"


def test_get_application_rejects_invalid_uuid(client):
    response = client.get("/api/applications/not-a-uuid")

    assert response.status_code == 422


# ============================
# Update Application Tests
# ============================

@patch("app.jobs.application_router.ApplicationService")
def test_update_application_status(mock_service_class, client):
    application = make_application(status="interview")

    service = mock_service_class.return_value
    service.update_application.return_value = application
    service.get_application.return_value = application_response(application)

    response = client.patch(
        f"/api/applications/{application.id}",
        json={"status": "interview"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "interview"

    kwargs = service.update_application.call_args.kwargs
    assert kwargs["status"] == "interview"
    assert kwargs["interview_at_provided"] is False


@patch("app.jobs.application_router.ApplicationService")
def test_update_application_sets_interview_time(
    mock_service_class,
    client,
):
    interview_at = datetime(2026, 10, 15, 10, 0, tzinfo=timezone.utc)
    application = make_application(
        status="interview",
        interview_at=interview_at,
    )

    service = mock_service_class.return_value
    service.update_application.return_value = application
    service.get_application.return_value = application_response(application)

    response = client.patch(
        f"/api/applications/{application.id}",
        json={"interview_at": interview_at.isoformat()},
    )

    assert response.status_code == 200
    assert response.json()["interview_at"] is not None

    kwargs = service.update_application.call_args.kwargs
    assert kwargs["interview_at_provided"] is True
    assert kwargs["interview_at"] == interview_at


@patch("app.jobs.application_router.ApplicationService")
def test_update_application_clears_interview_time(
    mock_service_class,
    client,
):
    application = make_application(interview_at=None)

    service = mock_service_class.return_value
    service.update_application.return_value = application
    service.get_application.return_value = application_response(application)

    response = client.patch(
        f"/api/applications/{application.id}",
        json={"interview_at": None},
    )

    assert response.status_code == 200
    assert response.json()["interview_at"] is None

    kwargs = service.update_application.call_args.kwargs
    assert kwargs["interview_at_provided"] is True
    assert kwargs["interview_at"] is None


@patch("app.jobs.application_router.ApplicationService")
def test_update_application_returns_404_when_missing(
    mock_service_class,
    client,
):
    mock_service_class.return_value.update_application.side_effect = (
        ValueError("Application not found")
    )

    response = client.patch(
        f"/api/applications/{uuid4()}",
        json={"status": "interview"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"


@patch("app.jobs.application_router.ApplicationService")
def test_update_application_returns_400_for_invalid_update(
    mock_service_class,
    client,
):
    mock_service_class.return_value.update_application.side_effect = (
        ValueError("Invalid application status")
    )

    response = client.patch(
        f"/api/applications/{uuid4()}",
        json={"status": "invalid-status"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid application status"


def test_update_application_rejects_invalid_uuid(client):
    response = client.patch(
        "/api/applications/not-a-uuid",
        json={"status": "interview"},
    )

    assert response.status_code == 422


# ============================
# Delete Application Tests
# ============================

@patch("app.jobs.application_router.ApplicationService")
def test_delete_application_success(mock_service_class, client):
    application_id = uuid4()

    response = client.delete(
        f"/api/applications/{application_id}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "application_id": str(application_id),
        "message": "Application deleted successfully",
    }

    mock_service_class.return_value.delete_application.assert_called_once()


@patch("app.jobs.application_router.ApplicationService")
def test_delete_application_returns_404_when_missing(
    mock_service_class,
    client,
):
    mock_service_class.return_value.delete_application.side_effect = (
        ValueError("Application not found")
    )

    response = client.delete(
        f"/api/applications/{uuid4()}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"


def test_delete_application_rejects_invalid_uuid(client):
    response = client.delete("/api/applications/not-a-uuid")

    assert response.status_code == 422