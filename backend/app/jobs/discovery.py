from sqlalchemy.orm import Session

from app.jobs.ingestion import DiscoveredJob
from app.jobs.service import JobService
from app.jobs.sources import JobSource


class JobDiscoveryService:

    def __init__(self, sources: list[JobSource]):
        self.sources = sources
        self.job_service = JobService()

    def discover_and_save(
        self,
        db: Session,
    ) -> list:
        saved_jobs = []

        for source in self.sources:
            jobs = source.fetch_jobs()

            for job in jobs:
                saved_job = self.job_service.save_discovered_job(
                    db=db,
                    discovered_job=job,
                )

                saved_jobs.append(saved_job)

        return saved_jobs