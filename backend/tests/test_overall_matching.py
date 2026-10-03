from app.jobs.overall_matching import (
    calculate_experience_score,
    calculate_overall_match_score,
)


def test_experience_score_compatible():
    assert calculate_experience_score("compatible") == 100


def test_experience_score_close():
    assert calculate_experience_score("close") == 75


def test_experience_score_below_requirement():
    assert calculate_experience_score("below_requirement") == 25


def test_experience_score_unknown():
    assert calculate_experience_score("unknown") is None


def test_overall_score_with_complete_data():
    result = calculate_overall_match_score(
        skill_score=80,
        skills_available=True,
        experience_fit="compatible",
    )

    assert result["overall_match_score"] == 86
    assert result["skill_match_score"] == 80
    assert result["experience_score"] == 100
    assert result["scoring_status"] == "complete"


def test_overall_score_skills_only():
    result = calculate_overall_match_score(
        skill_score=80,
        skills_available=True,
        experience_fit="unknown",
    )

    assert result["overall_match_score"] == 80
    assert result["skill_match_score"] == 80
    assert result["experience_score"] is None
    assert result["scoring_status"] == "skills_only"


def test_overall_score_experience_only():
    result = calculate_overall_match_score(
        skill_score=0,
        skills_available=False,
        experience_fit="compatible",
    )

    assert result["overall_match_score"] == 100
    assert result["skill_match_score"] is None
    assert result["experience_score"] == 100
    assert result["scoring_status"] == "experience_only"


def test_overall_score_insufficient_data():
    result = calculate_overall_match_score(
        skill_score=0,
        skills_available=False,
        experience_fit="unknown",
    )

    assert result["overall_match_score"] is None
    assert result["skill_match_score"] is None
    assert result["experience_score"] is None
    assert result["scoring_status"] == "insufficient_data"