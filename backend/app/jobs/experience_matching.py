import re
from datetime import date


MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def extract_experience_years(
    experience_text: str | None,
) -> float | None:

    if not experience_text:
        return None

    text = experience_text.lower()

    # ---------------------------------------------
    # 1. Explicit years
    # Examples:
    # 2 years
    # 3.5 years
    # 6+ years
    # ---------------------------------------------

    matches = re.findall(
        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)",
        text,
    )

    if matches:
        return max(float(value) for value in matches)

    # ---------------------------------------------
    # 2. Explicit months
    # Example:
    # 6 months internship
    # ---------------------------------------------

    month_matches = re.findall(
        r"(\d+)\s*(?:months?|mos?)",
        text,
    )

    if month_matches:
        months = max(int(value) for value in month_matches)
        return round(months / 12, 2)

    # ---------------------------------------------
    # 3. Date ranges
    # Examples:
    # Apr 2024 - Jun 2024
    # Apr 2024 – Jun 2024
    # January 2023 - March 2024
    # ---------------------------------------------

    date_pattern = re.compile(
        r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|"
        r"apr(?:il)?|may|jun(?:e)?|jul(?:y)?|"
        r"aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|"
        r"nov(?:ember)?|dec(?:ember)?)"
        r"\s+(\d{4})"
        r"\s*(?:-|–|—|to)\s*"
        r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|"
        r"apr(?:il)?|may|jun(?:e)?|jul(?:y)?|"
        r"aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|"
        r"nov(?:ember)?|dec(?:ember)?)"
        r"\s+(\d{4})",
        re.IGNORECASE,
    )

    date_ranges = date_pattern.findall(text)

    if date_ranges:
        total_months = 0

        for (
            start_month_text,
            start_year_text,
            end_month_text,
            end_year_text,
        ) in date_ranges:

            start_month = MONTHS[start_month_text.lower()]
            start_year = int(start_year_text)

            end_month = MONTHS[end_month_text.lower()]
            end_year = int(end_year_text)

            months = (
                (end_year - start_year) * 12
                + (end_month - start_month)
                + 1
            )

            if months > 0:
                total_months += months

        if total_months > 0:
            return round(total_months / 12, 2)

    return None


def experience_level_to_years(
    experience_level: str | None,
) -> float | None:

    if not experience_level:
        return None

    level = experience_level.lower().strip()

    mapping = {
        "internship": 0.0,
        "entry-level": 0.0,
        "junior": 1.0,
        "mid-level": 3.0,
        "senior": 5.0,
    }

    return mapping.get(level)


def calculate_experience_fit(
    resume_experience: str | None,
    job_experience_level: str | None,
    job_min_experience_years: float | None = None,
    job_max_experience_years: float | None = None,
) -> dict:
    candidate_years = extract_experience_years(resume_experience)

    # Prefer the structured numeric requirement when available.
    if job_min_experience_years is not None:
        required_years = job_min_experience_years

        if candidate_years is None:
            return {
                "experience_fit": "unknown",
                "candidate_experience_years": None,
                "required_experience_years": required_years,
            }

        if candidate_years < job_min_experience_years:
            # Allow a small gap when the candidate is close
            # to the minimum requirement.
            if candidate_years >= job_min_experience_years - 1:
                fit = "close"
            else:
                fit = "below_requirement"

        elif (
            job_max_experience_years is not None
            and candidate_years > job_max_experience_years
        ):
            fit = "above_range"

        else:
            fit = "compatible"

        return {
            "experience_fit": fit,
            "candidate_experience_years": candidate_years,
            "required_experience_years": required_years,
        }

    # Fall back to the existing experience-level logic
    # when the job has no numeric requirement.
    required_years = experience_level_to_years(job_experience_level)

    if required_years is None:
        return {
            "experience_fit": "unknown",
            "candidate_experience_years": candidate_years,
            "required_experience_years": None,
        }

    if candidate_years is None:
        return {
            "experience_fit": "unknown",
            "candidate_experience_years": None,
            "required_experience_years": required_years,
        }

    if candidate_years >= required_years:
        fit = "compatible"
    elif candidate_years >= required_years - 1:
        fit = "close"
    else:
        fit = "below_requirement"

    return {
        "experience_fit": fit,
        "candidate_experience_years": candidate_years,
        "required_experience_years": required_years,
    }