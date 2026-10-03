import uuid

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
    ):
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            scheduled_at=scheduled_at,
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        return notification

    def get_user_notifications(
        self,
        db: Session,
        user_id: uuid.UUID,
    ):
        return (
            db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .all()
        )

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