from datetime import datetime

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: str
    application_id: str | None = None
    title: str
    message: str
    notification_type: str
    scheduled_at: datetime | None
    is_read: bool
    is_sent: bool


class NotificationCreate(BaseModel):
    title: str
    message: str
    notification_type: str
    scheduled_at: datetime | None = None
    application_id: str | None = None