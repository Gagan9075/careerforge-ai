import pytest

from app.jobs.experience_extractor import (
    extract_experience_requirement,
)


@pytest.mark.parametrize(
    ("description", "expected_min", "expected_max", "expected_level"),
    [
        (
            "We need 3-5 years of experience.",
            3.0,
            5.0,
            "mid-level",
        ),
        (
            "Minimum 2 years of experience required.",
            2.0,
            None,
            "mid-level",
        ),
        (
            "Experience: 4 years.",
            4.0,
            4.0,
            "senior",
        ),
        (
            "Python internship available.",
            0.0,
            None,
            "internship",
        ),
        (
            "We welcome freshers.",
            0.0,
            None,
            "entry-level",
        ),
        (
            "Looking for a senior Python developer.",
            5.0,
            None,
            "senior",
        ),
        (
            "Python developer position.",
            None,
            None,
            None,
        ),
    ],
)
def test_extract_experience_requirement(
    description,
    expected_min,
    expected_max,
    expected_level,
):
    result = extract_experience_requirement(
        description=description,
        title="Python Developer",
    )

    assert result["min_years"] == expected_min
    assert result["max_years"] == expected_max
    assert result["experience_level"] == expected_level


def test_extract_experience_from_job_title():
    result = extract_experience_requirement(
        description="Python developer position.",
        title="Data Engineer (7.1-9 years)",
    )

    assert result["min_years"] == 7.1
    assert result["max_years"] == 9.0
    assert result["experience_level"] == "senior"