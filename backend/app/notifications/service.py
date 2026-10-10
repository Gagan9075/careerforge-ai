import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.notifications.model import Notification

class NotificationService:

    def create_notification(
        self,
        db: Session,
        user_id: uuid.UUID,
        title: str,
        message: str,
        notification_type: str,
        scheduled_at=None,
        application_id: uuid.UUID | None = None,
        commit: bool = True,
    ):
        notification = Notification(
            user_id=user_id,
            application_id=application_id,
            title=title,
            message=message,
            notification_type=notification_type,
            scheduled_at=scheduled_at,
        )

        db.add(notification)

        if commit:
            db.commit()
            db.refresh(notification)
        else:
            db.flush()

        return notification

    def get_user_notifications(
        self,
        db: Session,
        user_id: uuid.UUID,
    ):
        now = datetime.now(timezone.utc)

        return (
            db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                (
                    Notification.scheduled_at.is_(None)
                    | (Notification.scheduled_at <= now)
                ),
            )
            .order_by(Notification.created_at.desc())
            .all()
        )

    def process_due_notifications(
        self,
        db: Session,
    ) -> int:
        """
        Count notifications that are due and awaiting delivery.

        Actual delivery will be implemented separately.
        This method does not mark notifications as sent.
        """

        now = datetime.now(timezone.utc)

        due_notifications = (
            db.query(Notification)
            .filter(
                Notification.is_sent.is_(False),
                Notification.scheduled_at.is_not(None),
                Notification.scheduled_at <= now,
            )
            .all()
        )

        return len(due_notifications)

    def mark_as_read(
        self,
        db: Session,
        user_id: uuid.UUID,
        notification_id: uuid.UUID,
    ):
        notification = (
            db.query(Notification)
            .filter(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
            .first()
        )

        if not notification:
            raise ValueError("Notification not found")

        notification.is_read = True

        db.commit()
        db.refresh(notification)

        return notification

    def delete_notification(
        self,
        db: Session,
        user_id: uuid.UUID,
        notification_id: uuid.UUID,
    ):
        notification = (
            db.query(Notification)
            .filter(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
            .first()
        )

        if not notification:
            raise ValueError("Notification not found")

        db.delete(notification)
        db.commit()

        return True