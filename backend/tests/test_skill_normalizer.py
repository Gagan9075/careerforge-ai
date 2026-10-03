from app.jobs.skill_normalizer import parse_skills


resume_skills = """
Languages: Python, Java, C, JavaScript
Web: HTML, CSS, React, FastAPI, REST APIs
Database: PostgreSQL, MySQL, SQL
Cloud & Tools: Docker, Git, GitHub, Microsoft Azure, VS Code
"""

print(parse_skills(resume_skills))