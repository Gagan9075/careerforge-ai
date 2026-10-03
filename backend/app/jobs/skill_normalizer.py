import re


SKILL_ALIASES = {
    "postgres": "postgresql",
    "postgresql db": "postgresql",
    "postgres db": "postgresql",
    "js": "javascript",
    "javascript js": "javascript",
    "ts": "typescript",
    "react.js": "react",
    "reactjs": "react",
    "node.js": "node",
    "nodejs": "node",
    "express.js": "express",
    "expressjs": "express",
    "fast api": "fastapi",
    "rest api": "rest",
    "rest apis": "rest",
    "machine learning": "machine learning",
    "ml": "machine learning",
    "artificial intelligence": "ai",
    "ai": "ai",
}


def normalize_skill(skill: str) -> str:
    skill = skill.strip().lower()

    skill = re.sub(r"\s+", " ", skill)

    return SKILL_ALIASES.get(skill, skill)


def parse_skills(skills_text: str | None) -> list[str]:
    if not skills_text:
        return []

    normalized_skills = []

    # Process each line separately.
    for line in skills_text.splitlines():
        line = line.strip()

        if not line:
            continue

        # Remove section labels such as:
        # Languages:
        # Web:
        # Database:
        # Cloud & Tools:
        if ":" in line:
            _, line = line.split(":", 1)

        # Split individual skills.
        raw_skills = re.split(
            r"[,;|]",
            line,
        )

        for skill in raw_skills:
            normalized = normalize_skill(skill)

            if normalized and normalized not in normalized_skills:
                normalized_skills.append(normalized)

    return normalized_skills