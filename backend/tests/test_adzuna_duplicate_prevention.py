from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.jobs.schemas import JobCreate
from app.jobs.service import JobService


@pytest.fixture
def service():
    return JobService()


@pytest.fixture
def job_payload():
    return JobCreate(
        title="Python Developer",
        company="Capco",
        location="Bengaluru",
        description="Python development role",
        skills="Python, SQL",
        employment_type="Full-time",
        experience_level="Experienced",
        min_experience_years=3,
        max_experience_years=5,
        source="adzuna",
        source_url=(
            "https://www.adzuna.in/details/"
            "5888968631?utm_source=original"
        ),
        application_url=None,
        posted_at=datetime.now(timezone.utc),
    )


def make_existing_job(**overrides):
    values = {
        "id": uuid4(),
        "title": "Python Developer",
        "company": "Capco",
        "location": "Bengaluru",
        "description": "Old description",
        "skills": "Python",
        "employment_type": "Full-time",
        "experience_level": "Experienced",
        "min_experience_years": 3,
        "max_experience_years": 5,
        "source": "adzuna",
        "source_url": (
            "https://www.adzuna.in/details/"
            "5888968631?utm_source=old"
        ),
        "application_url": None,
        "posted_at": datetime.now(timezone.utc),
        "is_active": True,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (
            "https://www.adzuna.in/details/"
            "5888968631?utm_source=abc",
            "5888968631",
        ),
        (
            "https://www.adzuna.in/ad/"
            "5865064497?tracking=xyz",
            "5865064497",
        ),
        (
            "https://example.com/jobs/123",
            None,
        ),
        ("", None),
        (None, None),
    ],
)
def test_get_adzuna_id(service, url, expected):
    assert service._get_adzuna_id(url) == expected


def test_create_job_updates_existing_advertisement_with_different_tracking_url(
    service, job_payload
):
    existing = make_existing_job()
    db = MagicMock()

    db.query.return_value.filter.return_value.first.return_value = existing

    result = service.create_job(db, job_payload)

    assert result is existing
    assert result.source_url == job_payload.source_url
    assert result.description == job_payload.description

    db.add.assert_not_called()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(existing)


def test_create_job_does_not_match_different_advertisement_ids(
    service, job_payload
):
    existing = make_existing_job(
        source_url="https://www.adzuna.in/details/9999999999"
    )
    new_job = service.create_job(db, job_payload)

    assert new_job is not existing
    db.add.assert_called_once_with(new_job)
    db.commit.assert_called_once()


def test_create_job_keeps_non_adzuna_matching_behavior(
    service, job_payload
):
    job_payload.source = "test"
    job_payload.source_url = "https://example.com/jobs/1"

    existing = make_existing_job(
        source="test",
        source_url=job_payload.source_url,
    )
    db = MagicMock()

    db.query.return_value.filter.return_value.first.return_value = existing

    result = service.create_job(db, job_payload)

    assert result is existing
    db.commit.assert_called_once()