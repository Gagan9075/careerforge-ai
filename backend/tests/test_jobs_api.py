from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.jobs.router import router


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


def make_job(**overrides):
    now = datetime.now(timezone.utc)

    job = {
        "id": uuid4(),
        "title": "Python Developer",
        "company": "Example Technologies",
        "location": "Bengaluru",
        "description": "Develop backend applications using Python and FastAPI.",
        "skills": "Python, FastAPI, PostgreSQL",
        "employment_type": "Full-time",
        "experience_level": "Entry-level",
        "min_experience_years": 0.0,
        "max_experience_years": 2.0,
        "source": "test",
        "source_url": "https://example.com/jobs/python-developer",
        "application_url": "https://example.com/apply",
        "posted_at": now,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }

    job.update(overrides)
    return SimpleNamespace(**job)


def valid_job_payload(**overrides):
    payload = {
        "title": "Python Developer",
        "company": "Example Technologies",
        "location": "Bengaluru",
        "description": "Develop backend applications using Python and FastAPI.",
        "skills": "Python, FastAPI, PostgreSQL",
        "employment_type": "Full-time",
        "experience_level": "Entry-level",
        "min_experience_years": 0,
        "max_experience_years": 2,
        "source": "test",
        "source_url": "https://example.com/jobs/python-developer",
        "application_url": "https://example.com/apply",
    }

    payload.update(overrides)
    return payload


@patch("app.jobs.router.job_service.get_all_jobs")
def test_get_jobs_returns_jobs(mock_get_jobs, client):
    job = make_job()
    mock_get_jobs.return_value = [job]

    response = client.get("/api/jobs/")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == job.title
    assert response.json()[0]["company"] == job.company
    mock_get_jobs.assert_called_once()


@patch("app.jobs.router.job_service.get_all_jobs")
def test_get_jobs_returns_empty_list(mock_get_jobs, client):
    mock_get_jobs.return_value = []

    response = client.get("/api/jobs/")

    assert response.status_code == 200
    assert response.json() == []


@patch("app.jobs.router.job_service.search_jobs")
def test_search_jobs_by_keyword(mock_search_jobs, client):
    job = make_job()
    mock_search_jobs.return_value = [job]

    response = client.get(
        "/api/jobs/search",
        params={"search": "Python"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Python Developer"

    mock_search_jobs.assert_called_once()
    assert mock_search_jobs.call_args.kwargs["search"] == "Python"


@patch("app.jobs.router.job_service.search_jobs")
def test_search_jobs_with_all_filters(mock_search_jobs, client):
    mock_search_jobs.return_value = []

    response = client.get(
        "/api/jobs/search",
        params={
            "search": "Python",
            "location": "Bengaluru",
            "employment_type": "Full-time",
        },
    )

    assert response.status_code == 200
    assert response.json() == []

    kwargs = mock_search_jobs.call_args.kwargs
    assert kwargs["search"] == "Python"
    assert kwargs["location"] == "Bengaluru"
    assert kwargs["employment_type"] == "Full-time"


@patch("app.jobs.router.job_service.get_job_by_id")
def test_get_job_returns_job(mock_get_job, client):
    job = make_job()
    mock_get_job.return_value = job

    response = client.get(f"/api/jobs/{job.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(job.id)
    assert response.json()["title"] == job.title

    mock_get_job.assert_called_once()


@patch("app.jobs.router.job_service.get_job_by_id")
def test_get_job_returns_404_when_missing(mock_get_job, client):
    mock_get_job.return_value = None

    response = client.get(f"/api/jobs/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


@patch("app.jobs.router.job_service.create_job")
def test_create_job_success(mock_create_job, client):
    job = make_job()
    mock_create_job.return_value = job

    response = client.post(
        "/api/jobs/",
        json=valid_job_payload(),
    )

    assert response.status_code == 200
    assert response.json()["id"] == str(job.id)
    assert response.json()["title"] == job.title

    mock_create_job.assert_called_once()


def test_create_job_rejects_missing_required_field(client):
    payload = valid_job_payload()
    payload.pop("title")

    response = client.post("/api/jobs/", json=payload)

    assert response.status_code == 422


def test_create_job_rejects_empty_title(client):
    response = client.post(
        "/api/jobs/",
        json=valid_job_payload(title=""),
    )

    assert response.status_code == 422


@patch("app.jobs.router.job_service.deactivate_job")
def test_deactivate_job_success(mock_deactivate_job, client):
    job = make_job(is_active=False)
    mock_deactivate_job.return_value = job

    response = client.delete(f"/api/jobs/{job.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(job.id)
    assert response.json()["is_active"] is False

    mock_deactivate_job.assert_called_once()


@patch("app.jobs.router.job_service.deactivate_job")
def test_deactivate_job_returns_404_when_missing(
    mock_deactivate_job,
    client,
):
    mock_deactivate_job.return_value = None

    response = client.delete(f"/api/jobs/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_discover_jobs_rejects_short_role(client):
    response = client.post(
        "/api/jobs/discover",
        params={"role": "a"},
    )

    assert response.status_code == 422

# ============================
# Saved Jobs API Tests
# ============================

@patch("app.jobs.router.JobService.save_job")
def test_save_job_success(mock_save_job, client):
    job_id = uuid4()
    mock_save_job.return_value = SimpleNamespace(job_id=job_id)

    response = client.post(f"/api/jobs/{job_id}/save")

    assert response.status_code == 200
    assert response.json() == {
        "job_id": str(job_id),
        "message": "Job saved successfully",
    }

    mock_save_job.assert_called_once()


@patch("app.jobs.router.JobService.save_job")
def test_save_job_returns_404_when_job_missing(mock_save_job, client):
    mock_save_job.side_effect = ValueError("Job not found")
    job_id = uuid4()

    response = client.post(f"/api/jobs/{job_id}/save")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_save_job_rejects_invalid_uuid(client):
    response = client.post("/api/jobs/not-a-valid-uuid/save")

    assert response.status_code == 422


@patch("app.jobs.router.JobService.unsave_job")
def test_unsave_job_success(mock_unsave_job, client):
    job_id = uuid4()

    response = client.delete(f"/api/jobs/{job_id}/save")

    assert response.status_code == 200
    assert response.json() == {
        "job_id": str(job_id),
        "message": "Job removed from saved jobs",
    }

    mock_unsave_job.assert_called_once()


@patch("app.jobs.router.JobService.unsave_job")
def test_unsave_job_returns_404_when_not_saved(
    mock_unsave_job,
    client,
):
    mock_unsave_job.side_effect = ValueError("Saved job not found")
    job_id = uuid4()

    response = client.delete(f"/api/jobs/{job_id}/save")

    assert response.status_code == 404
    assert response.json()["detail"] == "Saved job not found"


@patch("app.jobs.router.JobService.get_saved_jobs")
def test_get_saved_jobs_returns_list(mock_get_saved_jobs, client):
    mock_get_saved_jobs.return_value = [
        {
            "job_id": str(uuid4()),
            "title": "Python Developer",
            "company": "Example Technologies",
            "location": "Bengaluru",
            "employment_type": "Full-time",
            "experience_level": "Entry-level",
            "min_experience_years": 0.0,
            "max_experience_years": 2.0,
            "source": "test",
            "source_url": "https://example.com/jobs/1",
            "application_url": "https://example.com/apply",
        }
    ]

    response = client.get("/api/jobs/saved")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Python Developer"
    assert response.json()[0]["company"] == "Example Technologies"

    mock_get_saved_jobs.assert_called_once()


@patch("app.jobs.router.JobService.get_saved_jobs")
def test_get_saved_jobs_returns_empty_list(mock_get_saved_jobs, client):
    mock_get_saved_jobs.return_value = []

    response = client.get("/api/jobs/saved")

    assert response.status_code == 200
    assert response.json() == []


# ============================
# Job Matching API Tests
# ============================

@patch("app.jobs.router.job_service.match_resume_with_job")
def test_match_job_returns_matching_results(
    mock_match_job,
    app,
    client,
):
    job_id = str(uuid4())

    expected_result = {
        "job_id": job_id,
        "job_title": "Python Developer",
        "company": "Example Technologies",
        "overall_match_score": 85,
        "skill_match_score": 90,
        "experience_score": 75,
        "match_score": 90,
        "matched_skills": ["Python", "FastAPI"],
        "missing_skills": ["Docker"],
        "skills_available": True,
        "experience_fit": "compatible",
        "candidate_experience_years": 1.0,
        "required_experience_min_years": 0.0,
        "required_experience_max_years": 2.0,
        "note": "Good skills match",
    }

    mock_match_job.return_value = expected_result

    mock_resume = SimpleNamespace(
        user_id=app.dependency_overrides[get_current_user]().id
    )

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = (
        mock_resume
    )

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get(f"/api/jobs/{job_id}/match")

    assert response.status_code == 200
    assert response.json()["job_id"] == job_id
    assert response.json()["overall_match_score"] == 85
    assert response.json()["matched_skills"] == ["Python", "FastAPI"]
    assert response.json()["missing_skills"] == ["Docker"]

    mock_match_job.assert_called_once()


def test_match_job_returns_404_when_resume_missing(app, client):
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get(f"/api/jobs/{uuid4()}/match")

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Resume not found. Please upload a resume first."
    )


@patch("app.jobs.router.job_service.match_resume_with_job")
def test_match_job_returns_404_when_job_missing(
    mock_match_job,
    app,
    client,
):
    mock_match_job.return_value = None

    mock_resume = SimpleNamespace(
        user_id=app.dependency_overrides[get_current_user]().id
    )

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = (
        mock_resume
    )

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get(f"/api/jobs/{uuid4()}/match")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found."