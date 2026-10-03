import re

from app.jobs.skill_normalizer import normalize_skill


KNOWN_SKILLS = {
    "python",
    "java",
    "c",
    "javascript",
    "typescript",
    "html",
    "css",
    "react",
    "angular",
    "fastapi",
    "flask",
    "django",
    "rest",
    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "redis",
    "docker",
    "kubernetes",
    "git",
    "github",
    "azure",
    "aws",
    "gcp",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "tensorflow",
    "pytorch",
    "spring",
    "spring boot",
    "hibernate",
    "c++",
    "c#",
    "node",
    "express",
    "graphql",
    "kafka",
    "terraform",
    "jenkins",
    "gitlab",
    "bitbucket",
    "selenium",
    "junit",
    "pandas",
    "numpy",
    "scikit-learn",
    "power bi",
    "tableau",
}


def extract_job_skills(description: str | None) -> list[str]:
    if not description:
        return []

    text = description.lower()

    # Normalize common variations before matching.
    text = re.sub(r"react\.js|reactjs", "react", text)
    text = re.sub(r"node\.js|nodejs", "node", text)
    text = re.sub(r"postgres\b", "postgresql", text)
    text = re.sub(r"rest apis?", "rest", text)
    text = re.sub(r"fast api", "fastapi", text)

    found_skills = []

    for skill in KNOWN_SKILLS:
        pattern = rf"(?<!\w){re.escape(skill)}(?!\w)"

        if re.search(pattern, text):
            normalized = normalize_skill(skill)

            if normalized not in found_skills:
                found_skills.append(normalized)

    return sorted(found_skills)