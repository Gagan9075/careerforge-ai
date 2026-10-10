import pytest

from app.jobs.skill_normalizer import normalize_skill, parse_skills


@pytest.mark.parametrize(
    ("skill", "expected"),
    [
        ("Python", "python"),
        ("  JavaScript  ", "javascript"),
        ("  Fast   API ", "fastapi"),
        ("Postgres", "postgresql"),
        ("postgres db", "postgresql"),
        ("React.js", "react"),
        ("ReactJS", "react"),
        ("Node.js", "node"),
        ("Express.js", "express"),
        ("REST APIs", "rest"),
        ("ML", "machine learning"),
        ("Artificial Intelligence", "ai"),
    ],
)
def test_normalize_skill(skill, expected):
    assert normalize_skill(skill) == expected


def test_parse_skills_from_resume_sections():
    resume_skills = """
    Languages: Python, Java, C, JavaScript
    Web: HTML, CSS, React, FastAPI, REST APIs
    Database: PostgreSQL, MySQL, SQL
    Cloud & Tools: Docker, Git, GitHub, Microsoft Azure, VS Code
    """

    result = parse_skills(resume_skills)

    assert "python" in result
    assert "javascript" in result
    assert "react" in result
    assert "fastapi" in result
    assert "rest" in result
    assert "postgresql" in result
    assert "microsoft azure" in result


def test_parse_skills_removes_duplicates():
    result = parse_skills("Python, python, PYTHON, Java")

    assert result == ["python", "java"]


def test_parse_skills_supports_multiple_separators():
    result = parse_skills("Python; Java | SQL, Docker")

    assert result == ["python", "java", "sql", "docker"]


def test_parse_skills_handles_empty_input():
    assert parse_skills(None) == []
    assert parse_skills("") == []


def test_parse_skills_handles_blank_lines():
    result = parse_skills(
        """
        Python, Java

        SQL, Docker
        """
    )

    assert result == ["python", "java", "sql", "docker"]


def test_normalize_skill_collapses_whitespace():
    assert normalize_skill("  machine    learning  ") == "machine learning"