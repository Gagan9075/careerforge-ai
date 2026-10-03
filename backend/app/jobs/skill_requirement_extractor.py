import re

from app.jobs.skill_extractor import extract_job_skills


REQUIRED_PATTERNS = [
    r"\bis\s+must\b",
    r"\bare\s+must\b",
    r"\bmust\b",
    r"\bmandatory\b",
    r"\brequired\b",
    r"\bcompulsory\b",
    r"\bessential\b",
]

PREFERRED_PATTERNS = [
    r"\bplus\b",
    r"\bpluses\b",
    r"\bpreferred\b",
    r"\bnice\s+to\s+have\b",
    r"\bgood\s+to\s+have\b",
    r"\bbonus\b",
]


def _contains_pattern(text: str, patterns: list[str]) -> bool:
    return any(
        re.search(pattern, text, re.IGNORECASE)
        for pattern in patterns
    )


def extract_skill_requirements(
    description: str | None,
) -> dict[str, list[str]]:

    if not description:
        return {
            "required_skills": [],
            "preferred_skills": [],
        }

    required_skills = set()
    preferred_skills = set()

    # Split the description into smaller pieces.
    sentences = re.split(
        r"(?<=[.!?])\s+|\n+",
        description,
    )

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        # Skills explicitly described as required.
        if _contains_pattern(
            sentence,
            REQUIRED_PATTERNS,
        ):
            skills = extract_job_skills(sentence)
            required_skills.update(skills)

        # Skills explicitly described as preferred.
        if _contains_pattern(
            sentence,
            PREFERRED_PATTERNS,
        ):
            skills = extract_job_skills(sentence)
            preferred_skills.update(skills)

    # Required takes priority over preferred.
    preferred_skills -= required_skills

    return {
        "required_skills": sorted(required_skills),
        "preferred_skills": sorted(preferred_skills),
    }