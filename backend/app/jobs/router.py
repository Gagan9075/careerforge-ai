import uuid

from fastapi import HTTPException
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.jobs.schemas import JobCreate, JobResponse
from app.jobs.service import JobService
from app.models.user import User

from app.jobs.discovery import JobDiscoveryService
from app.jobs.sources import AdzunaJobSource

from app.resume.model import Resume
from app.jobs.matching_schemas import JobMatchResponse


router = APIRouter(
    prefix="/api/jobs",
    tags=["Jobs"],
)

job_service = JobService()


@router.post("/", response_model=JobResponse)
def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return job_service.create_job(
        db=db,
        job_data=job_data,
    )


@router.get("/", response_model=list[JobResponse])
def get_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return job_service.get_all_jobs(db=db)


@router.post("/discover", response_model=list[JobResponse])
def discover_jobs(
    role: str = Query(..., min_length=2),
    location: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    discovery_service = JobDiscoveryService(
        sources=[
            AdzunaJobSource(
                search_term=role,
                location=location,
                results_per_page=10,
            )
        ]
    )

    return discovery_service.discover_and_save(db=db)


@router.get("/search", response_model=list[JobResponse])
def search_jobs(
    search: str | None = Query(default=None),
    location: str | None = Query(default=None),
    employment_type: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return job_service.search_jobs(
        db=db,
        search=search,
        location=location,
        employment_type=employment_type,
    )


@router.get(
    "/{job_id}/match",
    response_model=JobMatchResponse,
)
def match_job_with_resume(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = (
        db.query(Resume)
        .filter(
            Resume.user_id == current_user.id
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found. Please upload a resume first.",
        )

    result = job_service.match_resume_with_job(
        db=db,
        resume=resume,
        job_id=job_id,
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    return result

@router.post("/{job_id}/save")
def save_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = JobService()

    try:
        saved_job = service.save_job(
            db=db,
            user_id=current_user.id,
            job_id=job_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return {
        "job_id": str(saved_job.job_id),
        "message": "Job saved successfully",
    }


@router.delete("/{job_id}/save")
def unsave_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = JobService()

    try:
        service.unsave_job(
            db=db,
            user_id=current_user.id,
            job_id=job_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return {
        "job_id": str(job_id),
        "message": "Job removed from saved jobs",
    }


@router.get("/saved")
def get_saved_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = JobService()

    return service.get_saved_jobs(
        db=db,
        user_id=current_user.id,
    )

@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = job_service.get_job_by_id(
        db=db,
        job_id=job_id,
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return job



@router.delete("/{job_id}", response_model=JobResponse)
def deactivate_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = job_service.deactivate_job(
        db=db,
        job_id=job_id,
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return job


