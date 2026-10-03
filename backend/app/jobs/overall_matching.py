def calculate_experience_score(experience_fit: str) -> int | None:
    """
    Convert the existing experience-fit result into a numeric score.

    Returns None when there is not enough information to score experience.
    """

    score_map = {
        "compatible": 100,
        "close": 75,
        "above_range": 100,
        "below_requirement": 25,
    }

    return score_map.get(experience_fit)


def calculate_overall_match_score(
    skill_score: int | None,
    skills_available: bool,
    experience_fit: str,
) -> dict:
    """
    Combine skill matching and experience matching into
    one transparent overall match score.
    """

    experience_score = calculate_experience_score(experience_fit)

    has_skill_score = skills_available and skill_score is not None
    has_experience_score = experience_score is not None

    # --------------------------------------------------
    # Case 1: Both skill and experience information exist
    # --------------------------------------------------
    if has_skill_score and has_experience_score:
        overall_score = round(
            (skill_score * 0.70) +
            (experience_score * 0.30)
        )

        return {
            "overall_match_score": overall_score,
            "skill_match_score": skill_score,
            "experience_score": experience_score,
            "scoring_status": "complete",
        }

    # --------------------------------------------------
    # Case 2: Only skill information exists
    # --------------------------------------------------
    if has_skill_score:
        return {
            "overall_match_score": skill_score,
            "skill_match_score": skill_score,
            "experience_score": None,
            "scoring_status": "skills_only",
        }

    # --------------------------------------------------
    # Case 3: Only experience information exists
    # --------------------------------------------------
    if has_experience_score:
        return {
            "overall_match_score": experience_score,
            "skill_match_score": None,
            "experience_score": experience_score,
            "scoring_status": "experience_only",
        }

    # --------------------------------------------------
    # Case 4: Neither is available
    # --------------------------------------------------
    return {
        "overall_match_score": None,
        "skill_match_score": None,
        "experience_score": None,
        "scoring_status": "insufficient_data",
    }