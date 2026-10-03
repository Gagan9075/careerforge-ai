from app.jobs.skill_extractor import extract_job_skills


description = """
We are looking for a Python developer with
FastAPI, PostgreSQL, Docker and Git experience.
Knowledge of REST APIs is required.
"""

skills = extract_job_skills(description)

print(skills)