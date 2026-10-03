from app.jobs.matching import JobMatchingService


service = JobMatchingService()

result = service.calculate_match(
    resume_skills="Python, FastAPI, PostgreSQL, SQL, Git",
    job_skills="Python, Django, PostgreSQL, React, Docker",
)

print(result)