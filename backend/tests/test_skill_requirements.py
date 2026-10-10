import pytest

from app.jobs.skill_requirement_extractor import (
    extract_skill_requirements,
)


def test_extract_required_skills():
    description = (
        "Python and Django are required. "
        "FastAPI is mandatory. "
        "PostgreSQL is essential."
    )

    result = extract_skill_requirements(description)

    assert "python" in result["required_skills"]
    assert "django" in result["required_skills"]
    assert "fastapi" in result["required_skills"]
    assert "postgresql" in result["required_skills"]


def test_extract_preferred_skills():
    description = (
        "React is preferred. "
        "Docker is a plus. "
        "Knowledge of AWS is nice to have."
    )

    result = extract_skill_requirements(description)

    assert "react" in result["preferred_skills"]
    assert "docker" in result["preferred_skills"]
    assert "aws" in result["preferred_skills"]


def test_required_skills_are_not_duplicated_as_preferred():
    description = (
        "Python is required. "
        "Python is also preferred."
    )

    result = extract_skill_requirements(description)

    assert "python" in result["required_skills"]
    assert "python" not in result["preferred_skills"]


def test_extract_skills_from_newline_separated_description():
    description = """
    Python is required.
    Django is mandatory.
    Docker is preferred.
    """

    result = extract_skill_requirements(description)

    assert "python" in result["required_skills"]
    assert "django" in result["required_skills"]
    assert "docker" in result["preferred_skills"]


def test_matching_is_case_insensitive():
    description = (
        "PYTHON IS REQUIRED. "
        "Docker Is Preferred."
    )

    result = extract_skill_requirements(description)

    assert "python" in result["required_skills"]
    assert "docker" in result["preferred_skills"]


@pytest.mark.parametrize(
    "description",
    [
        None,
        "",
        "   ",
    ],
)
def test_empty_description_returns_empty_lists(description):
    result = extract_skill_requirements(description)

    assert result == {
        "required_skills": [],
        "preferred_skills": [],
    }


def test_description_without_requirement_keywords():
    description = (
        "We use Python, Django, PostgreSQL and Docker."
    )

    result = extract_skill_requirements(description)

    assert result == {
        "required_skills": [],
        "preferred_skills": [],
    }


def test_results_are_sorted():
    description = (
        "Python is required. "
        "Django is required. "
        "Docker is preferred. "
        "AWS is preferred."
    )

    result = extract_skill_requirements(description)

    assert result["required_skills"] == sorted(
        result["required_skills"]
    )
    assert result["preferred_skills"] == sorted(
        result["preferred_skills"]
    )