import pytest

from app.jobs.matching import JobMatchingService


@pytest.fixture
def service():
    return JobMatchingService()


def test_calculate_match_with_partial_overlap(service):
    result = service.calculate_match(
        resume_skills="Python, FastAPI, PostgreSQL, SQL, Git",
        job_skills="Python, Django, PostgreSQL, React, Docker",
    )

    assert result["match_score"] == 40
    assert result["matched_skills"] == ["postgresql", "python"]
    assert result["missing_skills"] == ["django", "docker", "react"]
    assert result["skills_available"] is True


def test_calculate_match_with_identical_skills(service):
    result = service.calculate_match(
        resume_skills="Python, FastAPI, PostgreSQL",
        job_skills="Python, FastAPI, PostgreSQL",
    )

    assert result["match_score"] == 100
    assert result["missing_skills"] == []
    assert result["skills_available"] is True


def test_calculate_match_with_no_overlap(service):
    result = service.calculate_match(
        resume_skills="Java, Spring Boot",
        job_skills="Python, Django",
    )

    assert result["match_score"] == 0
    assert result["matched_skills"] == []
    assert result["skills_available"] is True


def test_calculate_match_without_job_skills(service):
    result = service.calculate_match(
        resume_skills="Python, FastAPI",
        job_skills=None,
    )

    assert result["match_score"] == 0
    assert result["matched_skills"] == []
    assert result["missing_skills"] == []
    assert result["skills_available"] is False
    assert result["note"]