import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.notifications.schemas import (
    NotificationCreate,
    NotificationResponse,
)
from app.notifications.service import NotificationService


router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"],
)


@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_notification(
    data: NotificationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = NotificationService()

    notification = service.create_notification(
        db=db,
        user_id=current_user.id,
        title=data.title,
        message=data.message,
        notification_type=data.notification_type,
        scheduled_at=data.scheduled_at,
    )

    return {
        "id": str(notification.id),
        "title": notification.title,
        "message": notification.message,
        "notification_type": notification.notification_type,
        "scheduled_at": notification.scheduled_at,
        "is_read": notification.is_read,
        "is_sent": notification.is_sent,
    }


@router.get(
    "",
    response_model=list[NotificationResponse],
)
def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = NotificationService()

    notifications = service.get_user_notifications(
        db=db,
        user_id=current_user.id,
    )

    return [
        {
            "id": str(notification.id),
            "title": notification.title,
            "message": notification.message,
            "notification_type": notification.notification_type,
            "scheduled_at": notification.scheduled_at,
            "is_read": notification.is_read,
            "is_sent": notification.is_sent,
        }
        for notification in notifications
    ]


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_notification_as_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = NotificationService()

    try:
        notification = service.mark_as_read(
            db=db,
            user_id=current_user.id,
            notification_id=notification_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return {
        "id": str(notification.id),
        "title": notification.title,
        "message": notification.message,
        "notification_type": notification.notification_type,
        "scheduled_at": notification.scheduled_at,
        "is_read": notification.is_read,
        "is_sent": notification.is_sent,
    }


@router.delete(
    "/{notification_id}",
)
def delete_notification(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = NotificationService()

    try:
        service.delete_notification(
            db=db,
            user_id=current_user.id,
            notification_id=notification_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return {
        "notification_id": str(notification_id),
        "message": "Notification deleted successfully",
    }