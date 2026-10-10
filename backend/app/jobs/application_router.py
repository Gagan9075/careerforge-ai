import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.jobs.application_schemas import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
)
from app.jobs.application_service import ApplicationService
from app.models.user import User


router = APIRouter(
    prefix="/api/applications",
    tags=["Applications"],
)


@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_application(
    data: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ApplicationService()

    try:
        job_id = (
            uuid.UUID(data.job_id)
            if data.job_id
            else None
        )

        application = service.create_application(
            db=db,
            user_id=current_user.id,
            job_id=job_id,
            status=data.status,
            applied_at=data.applied_at,
            notes=data.notes,
            follow_up_at=data.follow_up_at,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return {
        "id": str(application.id),
        "job_id": (
            str(application.job_id)
            if application.job_id
            else None
        ),
        "title": None,
        "company": None,
        "status": application.status,
        "applied_at": application.applied_at,
        "notes": application.notes,
        "follow_up_at": application.follow_up_at,
        "interview_at": application.interview_at,
    }


@router.get(
    "",
    response_model=list[ApplicationResponse],
)
def get_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ApplicationService()

    return service.get_user_applications(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/{application_id}",
    response_model=ApplicationResponse,
)
def get_application(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ApplicationService()

    try:
        return service.get_application(
            db=db,
            user_id=current_user.id,
            application_id=application_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.patch(
    "/{application_id}",
    response_model=ApplicationResponse,
)
def update_application(
    application_id: uuid.UUID,
    data: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ApplicationService()

    try:
        update_fields = data.model_fields_set

        application = service.update_application(
            db=db,
            user_id=current_user.id,
            application_id=application_id,
            status=data.status,
            notes=data.notes,
            follow_up_at=data.follow_up_at,
            interview_at=data.interview_at,
            interview_at_provided=(
                "interview_at" in data.model_fields_set
            ),
        )

        return service.get_application(
            db=db,
            user_id=current_user.id,
            application_id=application.id,
        )

    except ValueError as exc:
        if str(exc) == "Application not found":
            raise HTTPException(
                status_code=404,
                detail=str(exc),
            )

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.delete(
    "/{application_id}",
)
def delete_application(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ApplicationService()

    try:
        service.delete_application(
            db=db,
            user_id=current_user.id,
            application_id=application_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return {
        "application_id": str(application_id),
        "message": "Application deleted successfully",
    }