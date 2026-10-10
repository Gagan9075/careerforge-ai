import pytest

from app.jobs.experience_matching import (
    extract_experience_years,
    experience_level_to_years,
    calculate_experience_fit,
)


# ---------------------------------------------
# Tests for experience extraction
# ---------------------------------------------

@pytest.mark.parametrize(
    ("experience_text", "expected"),
    [
        ("2 years of experience as a Python Developer", 2.0),
        ("3.5 years experience in software development", 3.5),
        ("6+ years of experience", 6.0),
        ("6 months internship", 0.5),
        ("18 months of experience", 1.5),
        ("No stated experience", None),
        ("", None),
        (None, None),
    ],
)
def test_extract_experience_years(experience_text, expected):
    assert extract_experience_years(experience_text) == expected


def test_extract_experience_from_date_range():
    result = extract_experience_years(
        "January 2023 - March 2024"
    )

    assert result == 1.25


def test_extract_experience_from_multiple_date_ranges():
    result = extract_experience_years(
        "Jan 2022 - Dec 2022; Jan 2024 - Dec 2024"
    )

    assert result == 2.0


# ---------------------------------------------
# Tests for experience-level conversion
# ---------------------------------------------

@pytest.mark.parametrize(
    ("level", "expected"),
    [
        ("internship", 0.0),
        ("entry-level", 0.0),
        ("junior", 1.0),
        ("mid-level", 3.0),
        ("senior", 5.0),
        (" Senior ", 5.0),
        ("unknown", None),
        (None, None),
    ],
)
def test_experience_level_to_years(level, expected):
    assert experience_level_to_years(level) == expected


# ---------------------------------------------
# Tests for experience fit
# ---------------------------------------------

def test_experience_fit_compatible():
    result = calculate_experience_fit(
        resume_experience="3 years of experience",
        job_experience_level="mid-level",
        job_min_experience_years=2.0,
        job_max_experience_years=5.0,
    )

    assert result["experience_fit"] == "compatible"
    assert result["candidate_experience_years"] == 3.0
    assert result["required_experience_years"] == 2.0


def test_experience_fit_close_to_minimum():
    result = calculate_experience_fit(
        resume_experience="2 years of experience",
        job_experience_level="mid-level",
        job_min_experience_years=3.0,
    )

    assert result["experience_fit"] == "close"


def test_experience_fit_below_requirement():
    result = calculate_experience_fit(
        resume_experience="1 year of experience",
        job_experience_level="senior",
        job_min_experience_years=4.0,
    )

    assert result["experience_fit"] == "below_requirement"


def test_experience_fit_above_maximum():
    result = calculate_experience_fit(
        resume_experience="8 years of experience",
        job_experience_level="mid-level",
        job_min_experience_years=2.0,
        job_max_experience_years=5.0,
    )

    assert result["experience_fit"] == "above_range"


def test_experience_fit_unknown_candidate_experience():
    result = calculate_experience_fit(
        resume_experience="Experience not mentioned",
        job_experience_level="senior",
        job_min_experience_years=5.0,
    )

    assert result["experience_fit"] == "unknown"
    assert result["candidate_experience_years"] is None
    assert result["required_experience_years"] == 5.0


def test_experience_fit_uses_job_level_fallback():
    result = calculate_experience_fit(
        resume_experience="4 years of experience",
        job_experience_level="mid-level",
    )

    assert result["experience_fit"] == "compatible"
    assert result["candidate_experience_years"] == 4.0
    assert result["required_experience_years"] == 3.0


def test_experience_fit_unknown_job_requirement():
    result = calculate_experience_fit(
        resume_experience="4 years of experience",
        job_experience_level=None,
    )

    assert result["experience_fit"] == "unknown"
    assert result["candidate_experience_years"] == 4.0
    assert result["required_experience_years"] is None