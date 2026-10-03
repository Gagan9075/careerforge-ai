from app.jobs.sources import AdzunaJobSource
from app.jobs.experience_extractor import (
    extract_experience_requirement,
)


source = AdzunaJobSource(
    search_term="python developer",
    location="Bengaluru",
    results_per_page=10,
)

jobs = source.fetch_jobs()

for job in jobs:
    result = extract_experience_requirement(
        description=job.description,
        title=job.title,
    )

    print("\n" + "=" * 70)
    print("JOB:", job.title)
    print("COMPANY:", job.company)
    print("CURRENT LEVEL:", job.experience_level)
    print("DETAILED REQUIREMENT:", result)

    if result["min_years"] is None:
        print("\nFULL DESCRIPTION:")
        print(job.description)