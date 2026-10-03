import re


def extract_experience_requirement(
    description: str | None,
    title: str | None = None,
) -> dict:

    text = description.lower() if description else ""
    title_text = title.lower() if title else ""

    # -------------------------------------------------
    # 1. Explicit ranges
    #
    # Examples:
    # 3-5 years
    # 3 – 6 years
    # 6 yrs - 7 yrs
    # 7.1-9 years
    # 2 to 4 years
    # -------------------------------------------------

    ranges = re.findall(
        r"\b(\d+(?:\.\d+)?)\s*(?:years?|yrs?)?\s*"
        r"(?:-|–|—|to)\s*"
        r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\b",
        text,
    )

    if ranges:
        min_years = min(
            float(start)
            for start, _ in ranges
        )

        max_years = max(
            float(end)
            for _, end in ranges
        )

        return {
            "min_years": min_years,
            "max_years": max_years,
            "experience_level": _level_from_years(min_years),
        }

    # -------------------------------------------------
    # 2. Minimum experience
    #
    # Examples:
    # 3+ years
    # minimum 3 years
    # at least 3 years
    # -------------------------------------------------

    minimum_patterns = [
        r"\b(\d+(?:\.\d+)?)\s*\+\s*(?:years?|yrs?)\b",

        r"\b(?:minimum|min\.?|at least)\s+"
        r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\b",

        r"\b(\d+(?:\.\d+)?)\s*(?:years?|yrs?)"
        r"\s*(?:or more|and above)\b",
    ]

    for pattern in minimum_patterns:
        match = re.search(pattern, text)

        if match:
            min_years = float(match.group(1))

            return {
                "min_years": min_years,
                "max_years": None,
                "experience_level": _level_from_years(min_years),
            }

    # -------------------------------------------------
    # 3. Experience / Exp followed by a number
    #
    # Examples:
    # Experience - 7 years
    # Experience: 7 years
    # Exp- 3 years
    # -------------------------------------------------

    experience_label_match = re.search(
        r"\b(?:experience|exp)\s*[:\-]?\s*"
        r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\b",
        text,
    )

    if experience_label_match:
        years = float(
            experience_label_match.group(1)
        )

        return {
            "min_years": years,
            "max_years": years,
            "experience_level": _level_from_years(years),
        }

    # -------------------------------------------------
    # 4. Generic exact experience
    #
    # Examples:
    # 2 years of experience
    # 2 years experience
    # -------------------------------------------------

    exact_match = re.search(
        r"\b(\d+(?:\.\d+)?)\s*"
        r"(?:years?|yrs?)"
        r"(?:\s+of)?\s+experience\b",
        text,
    )

    if exact_match:
        years = float(
            exact_match.group(1)
        )

        return {
            "min_years": years,
            "max_years": years,
            "experience_level": _level_from_years(years),
        }

    # -------------------------------------------------
    # 5. Internship
    # -------------------------------------------------

    if re.search(
        r"\b(intern|internship|trainee)\b",
        text,
    ):
        return {
            "min_years": 0.0,
            "max_years": None,
            "experience_level": "internship",
        }

    # -------------------------------------------------
    # 6. Fresher / entry-level
    # -------------------------------------------------

    if re.search(
        r"\b(fresher|freshers|entry[- ]level|graduate|graduates)\b",
        text,
    ):
        return {
            "min_years": 0.0,
            "max_years": None,
            "experience_level": "entry-level",
        }

    # -------------------------------------------------
    # 7. Seniority keywords
    # -------------------------------------------------

    if re.search(
        r"\b(senior|sr\.?)\b",
        text,
    ):
        return {
            "min_years": 5.0,
            "max_years": None,
            "experience_level": "senior",
        }

    if re.search(
        r"\b(junior|jr\.?|associate)\b",
        text,
    ):
        return {
            "min_years": 1.0,
            "max_years": 3.0,
            "experience_level": "junior",
        }

    if re.search(
        r"\b(mid[- ]level)\b",
        text,
    ):
        return {
            "min_years": 3.0,
            "max_years": 5.0,
            "experience_level": "mid-level",
        }

    # -------------------------------------------------
    # 8. Job title fallback
    #
    # Example:
    # "Data Engineer (7.1-9 years)"
    # -------------------------------------------------

    if title_text:
        title_result = _extract_numeric_requirement(
            title_text
        )

        if title_result:
            return title_result

    return {
        "min_years": None,
        "max_years": None,
        "experience_level": None,
    }


def _extract_numeric_requirement(
    text: str,
) -> dict | None:

    # Range
    ranges = re.findall(
        r"\b(\d+(?:\.\d+)?)\s*(?:-|–|—|to)\s*"
        r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\b",
        text,
    )

    if ranges:
        min_years = min(
            float(start)
            for start, _ in ranges
        )

        max_years = max(
            float(end)
            for _, end in ranges
        )

        return {
            "min_years": min_years,
            "max_years": max_years,
            "experience_level": _level_from_years(min_years),
        }

    # Single number
    match = re.search(
        r"\b(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\b",
        text,
    )

    if match:
        years = float(match.group(1))

        return {
            "min_years": years,
            "max_years": years,
            "experience_level": _level_from_years(years),
        }

    return None


def _level_from_years(years: float) -> str:
    if years <= 0:
        return "entry-level"

    if years <= 1:
        return "junior"

    if years <= 3:
        return "mid-level"

    if years <= 5:
        return "senior"

    return "senior"


def extract_experience_level(
    description: str | None,
) -> str | None:
    """
    Backward-compatible function used by job ingestion.
    """

    result = extract_experience_requirement(description)

    return result["experience_level"]