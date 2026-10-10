from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.notifications.model import Notification
from app.notifications.service import NotificationService


@pytest.fixture
def service():
    return NotificationService()


@pytest.fixture
def db():
    return MagicMock()


# --------------------------------------------------
# Create notification
# --------------------------------------------------

def test_create_notification_commits_and_refreshes(service, db):
    user_id = uuid4()
    application_id = uuid4()
    scheduled_at = datetime.now(timezone.utc)

    notification = service.create_notification(
        db=db,
        user_id=user_id,
        application_id=application_id,
        title="Interview Reminder",
        message="Your interview is scheduled soon.",
        notification_type="interview_reminder",
        scheduled_at=scheduled_at,
    )

    db.add.assert_called_once_with(notification)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(notification)

    assert notification.user_id == user_id
    assert notification.application_id == application_id
    assert notification.title == "Interview Reminder"
    assert notification.notification_type == "interview_reminder"
    assert notification.scheduled_at == scheduled_at


def test_create_notification_without_commit(service, db):
    notification = service.create_notification(
        db=db,
        user_id=uuid4(),
        title="Test Notification",
        message="Testing notification creation.",
        notification_type="test",
        commit=False,
    )

    db.add.assert_called_once_with(notification)
    db.flush.assert_called_once()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()


# --------------------------------------------------
# Retrieve user notifications
# --------------------------------------------------

def test_get_user_notifications_returns_query_results(service, db):
    expected_notifications = [
        MagicMock(spec=Notification),
        MagicMock(spec=Notification),
    ]

    query = db.query.return_value
    query.filter.return_value.order_by.return_value.all.return_value = (
        expected_notifications
    )

    result = service.get_user_notifications(db, uuid4())

    assert result == expected_notifications
    db.query.assert_called_once_with(Notification)
    query.filter.assert_called_once()
    query.filter.return_value.order_by.assert_called_once()


# --------------------------------------------------
# Process due notifications
# --------------------------------------------------

def test_process_due_notifications_returns_due_count(service, db):
    due_notifications = [
        MagicMock(spec=Notification),
        MagicMock(spec=Notification),
    ]

    db.query.return_value.filter.return_value.all.return_value = (
        due_notifications
    )

    result = service.process_due_notifications(db)

    assert result == 2
    db.query.assert_called_once_with(Notification)


def test_process_due_notifications_returns_zero_when_none_are_due(
    service, db
):
    db.query.return_value.filter.return_value.all.return_value = []

    result = service.process_due_notifications(db)

    assert result == 0


# --------------------------------------------------
# Mark notification as read
# --------------------------------------------------

def test_mark_notification_as_read(service, db):
    user_id = uuid4()
    notification_id = uuid4()

    notification = MagicMock(spec=Notification)
    notification.is_read = False

    db.query.return_value.filter.return_value.first.return_value = (
        notification
    )

    result = service.mark_as_read(
        db=db,
        user_id=user_id,
        notification_id=notification_id,
    )

    assert result is notification
    assert notification.is_read is True
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(notification)


def test_mark_notification_as_read_raises_when_not_found(service, db):
    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(ValueError, match="Notification not found"):
        service.mark_as_read(
            db=db,
            user_id=uuid4(),
            notification_id=uuid4(),
        )

    db.commit.assert_not_called()


# --------------------------------------------------
# Delete notification
# --------------------------------------------------

def test_delete_notification(service, db):
    notification = MagicMock(spec=Notification)

    db.query.return_value.filter.return_value.first.return_value = (
        notification
    )

    result = service.delete_notification(
        db=db,
        user_id=uuid4(),
        notification_id=uuid4(),
    )

    assert result is True
    db.delete.assert_called_once_with(notification)
    db.commit.assert_called_once()


def test_delete_notification_raises_when_not_found(service, db):
    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(ValueError, match="Notification not found"):
        service.delete_notification(
            db=db,
            user_id=uuid4(),
            notification_id=uuid4(),
        )

    db.delete.assert_not_called()
    db.commit.assert_not_called()