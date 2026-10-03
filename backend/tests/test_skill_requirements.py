from app.jobs.skill_requirement_extractor import (
    extract_skill_requirements,
)


description = """
Flask, Django or similar python micro-framework
Experience in Linux
Experience with MongoDB
HTML5, API and Angular 2.0 is must
Bootstrap, jQuery and similar javascript framework are pluses.
"""

result = extract_skill_requirements(description)

print(result)
