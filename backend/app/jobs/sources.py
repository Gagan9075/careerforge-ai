from abc import ABC, abstractmethod
from datetime import datetime

import httpx

from app.core.config import settings
from app.jobs.ingestion import DiscoveredJob

from app.jobs.skill_extractor import extract_job_skills
from app.jobs.experience_extractor import extract_experience_level
from app.jobs.experience_extractor import extract_experience_requirement


class JobSource(ABC):
    @abstractmethod
    def fetch_jobs(self) -> list[DiscoveredJob]:
        raise NotImplementedError


class SampleJobSource(JobSource):
    def fetch_jobs(self) -> list[DiscoveredJob]:
        from app.jobs.ingestion import get_sample_jobs

        return get_sample_jobs()


class AdzunaJobSource(JobSource):
    def __init__(
        self,
        country: str = "in",
        search_term: str = "python developer",
        location: str = "Bengaluru",
        results_per_page: int = 10,
    ):
        self.country = country
        self.search_term = search_term
        self.location = location
        self.results_per_page = results_per_page

    def fetch_jobs(self) -> list[DiscoveredJob]:
        url = (
            f"https://api.adzuna.com/v1/api/jobs/"
            f"{self.country}/search/1"
        )

        params = {
            "app_id": settings.adzuna_app_id,
            "app_key": settings.adzuna_app_key,
            "results_per_page": self.results_per_page,
            "what": self.search_term,
            "where": self.location,
            "content-type": "application/json",
        }

        response = httpx.get(
            url,
            params=params,
            timeout=20.0,
        )

        response.raise_for_status()

        data = response.json()

        discovered_jobs = []

        for item in data.get("results", []):
            company = item.get("company") or {}
            location = item.get("location") or {}

            created_at = item.get("created")
            posted_at = None

            if created_at:
                try:
                    posted_at = datetime.fromisoformat(
                        created_at.replace("Z", "+00:00")
                    )
                except ValueError:
                    posted_at = None

            description = item.get("description", "")
            title = item.get("title", "Untitled Job")

            experience_requirement = extract_experience_requirement(
                description=description,
                title=title,
            )

            discovered_jobs.append(
                DiscoveredJob(
                    title=title,
                    company=company.get("display_name", "Unknown Company"),
                    location=location.get("display_name"),
                    description=description,
                    skills=", ".join(
                        extract_job_skills(description)
                    ),
                    employment_type=item.get("contract_type"),

                    experience_level=experience_requirement["experience_level"],
                    min_experience_years=experience_requirement["min_years"],
                    max_experience_years=experience_requirement["max_years"],

                    source="adzuna",
                    source_url=item.get("redirect_url", ""),
                    application_url=None,
                    posted_at=posted_at,
                )
            )

        return discovered_jobs