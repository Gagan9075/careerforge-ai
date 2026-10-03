from dataclasses import dataclass
from datetime import datetime


@dataclass
class DiscoveredJob:
    title: str
    company: str
    location: str | None
    description: str
    skills: str | None
    employment_type: str | None
    experience_level: str | None

    # New: structured experience requirement
    min_experience_years: float | None
    max_experience_years: float | None

    source: str
    source_url: str
    application_url: str | None
    posted_at: datetime | None