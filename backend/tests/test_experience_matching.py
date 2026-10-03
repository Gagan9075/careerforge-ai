from app.jobs.experience_matching import (
    extract_experience_years,
    calculate_experience_fit,
)


tests = [
    "2 years of experience as a Python Developer",
    "3.5 years experience in software development",
    "6+ years of experience",
    "6 months internship",
    "Apr 2024 – Jun 2024",
    "January 2023 - March 2024",
    "Software developer with no stated experience",
]


for text in tests:
    print(
        text,
        "=>",
        extract_experience_years(text),
    )


print(
    calculate_experience_fit(
        "Apr 2024 – Jun 2024",
        "senior",
    )
)