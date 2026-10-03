import uuid
from sqlalchemy.orm import Session

from app.jobs.model import Job
from app.jobs.schemas import JobCreate

from app.jobs.ingestion import DiscoveredJob

from sqlalchemy import or_

from app.jobs.matching import JobMatchingService
from app.resume.model import Resume

from app.jobs.experience_matching import calculate_experience_fit
from app.jobs.overall_matching import calculate_overall_match_score

from app.jobs.saved_job_model import SavedJob

class JobService:

    def __init__(self):
        self.matcher = JobMatchingService()

    def create_job(self, db: Session, job_data: JobCreate) -> Job:
        existing_job = (
            db.query(Job)
            .filter(
                Job.title == job_data.title,
                Job.company == job_data.company,
                Job.source_url == job_data.source_url,
            )
            .first()
        )

        if existing_job:
            existing_job.description = job_data.description
            existing_job.skills = job_data.skills
            existing_job.location = job_data.location
            existing_job.employment_type = job_data.employment_type
            existing_job.experience_level = job_data.experience_level
            existing_job.min_experience_years = job_data.min_experience_years
            existing_job.max_experience_years = job_data.max_experience_years
            existing_job.source_url = job_data.source_url
            existing_job.posted_at = job_data.posted_at
            existing_job.is_active = True

            if job_data.application_url:
                existing_job.application_url = job_data.application_url

            db.commit()
            db.refresh(existing_job)

            return existing_job

        job = Job(
            title=job_data.title,
            company=job_data.company,
            location=job_data.location,
            description=job_data.description,
            skills=job_data.skills,
            employment_type=job_data.employment_type,
            experience_level=job_data.experience_level,
            min_experience_years=job_data.min_experience_years,
            max_experience_years=job_data.max_experience_years,
            source=job_data.source,
            source_url=job_data.source_url,
            application_url=job_data.application_url,
            posted_at=job_data.posted_at,
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        return job

    def get_all_jobs(self, db: Session) -> list[Job]:
        return (
            db.query(Job)
            .filter(Job.is_active.is_(True))
            .order_by(Job.created_at.desc())
            .all()
        )

    def get_job_by_id(self, db: Session, job_id: str) -> Job | None:
        return (
            db.query(Job)
            .filter(
                Job.id == job_id,
                Job.is_active.is_(True),
            )
            .first()
        )

    def deactivate_job(self, db: Session, job_id: str) -> Job | None:
        job = (
            db.query(Job)
            .filter(Job.id == job_id)
            .first()
        )

        if not job:
            return None

        job.is_active = False

        db.commit()
        db.refresh(job)

        return job

    def save_discovered_job(
        self,
        db: Session,
        discovered_job: DiscoveredJob,
    ) -> Job:
        job_data = JobCreate(
            title=discovered_job.title,
            company=discovered_job.company,
            location=discovered_job.location,
            description=discovered_job.description,
            skills=discovered_job.skills,
            employment_type=discovered_job.employment_type,
            experience_level=discovered_job.experience_level,
            min_experience_years=discovered_job.min_experience_years,
            max_experience_years=discovered_job.max_experience_years,
            source=discovered_job.source,
            source_url=discovered_job.source_url,
            application_url=discovered_job.application_url,
            posted_at=discovered_job.posted_at,
        )

        return self.create_job(
            db=db,
            job_data=job_data,
        )

    def search_jobs(
        self,
        db: Session,
        search: str | None = None,
        location: str | None = None,
        employment_type: str | None = None,
    ) -> list[Job]:

        query = db.query(Job).filter(
            Job.is_active.is_(True)
        )

        if search:
            search_term = f"%{search}%"

            query = query.filter(
                or_(
                    Job.title.ilike(search_term),
                    Job.company.ilike(search_term),
                    Job.description.ilike(search_term),
                )
            )

        if location:
            query = query.filter(
                Job.location.ilike(f"%{location}%")
            )

        if employment_type:
            query = query.filter(
                Job.employment_type.ilike(
                    f"%{employment_type}%"
                )
            )

        return query.order_by(
            Job.created_at.desc()
        ).all()

    def match_resume_with_job(
        self,
        db: Session,
        resume: Resume,
        job_id: str,
    ):
        job = self.get_job_by_id(db, job_id)

        if not job:
            return None

        # -----------------------------
        # 1. Skill matching
        # -----------------------------
        match_result = self.matcher.calculate_match(
            resume_skills=resume.skills,
            job_skills=job.skills,
        )

        # -----------------------------
        # 2. Experience matching
        # -----------------------------
        experience_result = calculate_experience_fit(
            resume_experience=resume.experience,
            job_experience_level=job.experience_level,
            job_min_experience_years=job.min_experience_years,
            job_max_experience_years=job.max_experience_years,
        )

        overall_result = calculate_overall_match_score(
            skill_score=match_result["match_score"],
            skills_available=match_result["skills_available"],
            experience_fit=experience_result["experience_fit"],
        )

        # -----------------------------
        # 3. Combined response
        # -----------------------------
        return {
            "job_id": str(job.id),
            "job_title": job.title,
            "company": job.company,

            # Skill matching
            "match_score": match_result["match_score"],
            "overall_match_score": overall_result["overall_match_score"],
            "skill_match_score": overall_result["skill_match_score"],
            "experience_score": overall_result["experience_score"],

            "matched_skills": match_result["matched_skills"],

            "missing_skills": match_result["missing_skills"],
            "skills_available": match_result["skills_available"],

            # Experience matching
            "experience_fit": experience_result["experience_fit"],
            "candidate_experience_years": (
                experience_result["candidate_experience_years"]
            ),
            "required_experience_min_years": (
                job.min_experience_years
            ),
            "required_experience_max_years": (
                job.max_experience_years
            ),

            # Explanation
            "note": match_result["note"],
        }

    def save_job(self, db: Session, user_id: uuid.UUID, job_id: uuid.UUID):
        job = db.query(Job).filter(Job.id == job_id).first()

        if not job:
            raise ValueError("Job not found")

        existing = (
            db.query(SavedJob)
            .filter(
                SavedJob.user_id == user_id,
                SavedJob.job_id == job_id,
            )
            .first()
        )

        if existing:
            return existing

        saved_job = SavedJob(
            user_id=user_id,
            job_id=job_id,
        )

        db.add(saved_job)
        db.commit()
        db.refresh(saved_job)

        return saved_job


    def unsave_job(self, db: Session, user_id: uuid.UUID, job_id: uuid.UUID):
        saved_job = (
            db.query(SavedJob)
            .filter(
                SavedJob.user_id == user_id,
                SavedJob.job_id == job_id,
            )
            .first()
        )

        if not saved_job:
            raise ValueError("Saved job not found")

        db.delete(saved_job)
        db.commit()

        return True


    def get_saved_jobs(
        self,
        db: Session,
        user_id: uuid.UUID,
    ):
        saved_jobs = (
            db.query(SavedJob, Job)
            .join(Job, SavedJob.job_id == Job.id)
            .filter(SavedJob.user_id == user_id)
            .order_by(SavedJob.created_at.desc())
            .all()
        )

        return [
            {
                "job_id": str(saved_job.job_id),
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "employment_type": job.employment_type,
                "experience_level": job.experience_level,
                "min_experience_years": job.min_experience_years,
                "max_experience_years": job.max_experience_years,
                "source": job.source,
                "source_url": job.source_url,
                "application_url": job.application_url,
            }
            for saved_job, job in saved_jobs
        ]