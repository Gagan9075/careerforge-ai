from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.jobs.application_service import ApplicationService
from app.jobs.application_model import Application
from app.jobs.model import Job
from app.notifications.model import Notification


@pytest.fixture
def setup_application():
    user_id = uuid4()
    application_id = uuid4()
    job_id = uuid4()

    application = SimpleNamespace(
        id=application_id,
        user_id=user_id,
        job_id=job_id,
        status="applied",
        notes="Test application",
        follow_up_at=None,
        interview_at=None,
        applied_at=datetime.now(timezone.utc),
    )

    job = SimpleNamespace(
        id=job_id,
        title="Python Developer",
        company="Example Technologies",
    )

    db = MagicMock()

    # First query: find the application.
    # Subsequent queries: find pending reminders or the related job.
    db.query.return_value.filter.return_value.first.side_effect = [
        application,
        job,
    ]

    db.query.return_value.filter.return_value.all.return_value = []

    return SimpleNamespace(
        db=db,
        user_id=user_id,
        application_id=application_id,
        application=application,
        job=job,
    )


def test_schedule_interview_creates_reminder_24_hours_before(
    setup_application,
):
    data = setup_application

    interview_at = datetime.now(timezone.utc) + timedelta(days=3)

    with patch(
        "app.jobs.application_service.NotificationService"
    ) as notification_service_class:
        service = ApplicationService()

        result = service.update_application(
            db=data.db,
            user_id=data.user_id,
            application_id=data.application_id,
            interview_at=interview_at,
            interview_at_provided=True,
        )

    assert result.interview_at == interview_at

    notification_service_class.return_value.create_notification.assert_called_once()

    kwargs = (
        notification_service_class
        .return_value
        .create_notification
        .call_args.kwargs
    )

    assert kwargs["user_id"] == data.user_id
    assert kwargs["application_id"] == data.application_id
    assert kwargs["title"] == "Interview Reminder"
    assert kwargs["notification_type"] == "interview_reminder"
    assert kwargs["commit"] is False

    expected_reminder = interview_at - timedelta(hours=24)

    assert abs(
        (kwargs["scheduled_at"] - expected_reminder).total_seconds()
    ) < 1

    data.db.commit.assert_called_once()
    data.db.refresh.assert_called_once_with(data.application)


def test_schedule_interview_soon_schedules_immediate_reminder(
    setup_application,
):
    data = setup_application

    interview_at = datetime.now(timezone.utc) + timedelta(hours=2)

    with patch(
        "app.jobs.application_service.NotificationService"
    ) as notification_service_class:
        service = ApplicationService()

        service.update_application(
            db=data.db,
            user_id=data.user_id,
            application_id=data.application_id,
            interview_at=interview_at,
            interview_at_provided=True,
        )

    kwargs = (
        notification_service_class
        .return_value
        .create_notification
        .call_args.kwargs
    )

    # The normal 24-hour deadline has already passed.
    # Therefore, the reminder should be due immediately.
    assert kwargs["scheduled_at"] <= datetime.now(timezone.utc)
    assert kwargs["scheduled_at"] >= (
        datetime.now(timezone.utc) - timedelta(seconds=5)
    )


def test_past_interview_does_not_create_reminder(setup_application):
    data = setup_application

    interview_at = datetime.now(timezone.utc) - timedelta(hours=1)

    with patch(
        "app.jobs.application_service.NotificationService"
    ) as notification_service_class:
        service = ApplicationService()

        service.update_application(
            db=data.db,
            user_id=data.user_id,
            application_id=data.application_id,
            interview_at=interview_at,
            interview_at_provided=True,
        )

    notification_service_class.return_value.create_notification.assert_not_called()

    assert data.application.interview_at == interview_at
    data.db.commit.assert_called_once()


def test_interview_without_timezone_is_rejected(setup_application):
    data = setup_application

    interview_at = datetime(2026, 10, 15, 10, 0)

    service = ApplicationService()

    with pytest.raises(
        ValueError,
        match="Interview date must include a timezone",
    ):
        service.update_application(
            db=data.db,
            user_id=data.user_id,
            application_id=data.application_id,
            interview_at=interview_at,
            interview_at_provided=True,
        )

    data.db.rollback.assert_called_once()
    data.db.commit.assert_not_called()


def test_clearing_interview_removes_pending_reminders(
    setup_application,
):
    data = setup_application

    reminder = SimpleNamespace(
        id=uuid4(),
        application_id=data.application_id,
        user_id=data.user_id,
        notification_type="interview_reminder",
        is_sent=False,
    )

    data.db.query.return_value.filter.return_value.all.return_value = [
        reminder
    ]

    service = ApplicationService()

    result = service.update_application(
        db=data.db,
        user_id=data.user_id,
        application_id=data.application_id,
        interview_at=None,
        interview_at_provided=True,
    )

    assert result.interview_at is None

    data.db.delete.assert_called_once_with(reminder)
    data.db.commit.assert_called_once()


def test_omitting_interview_field_preserves_existing_interview(
    setup_application,
):
    data = setup_application

    existing_interview = datetime.now(timezone.utc) + timedelta(days=2)
    data.application.interview_at = existing_interview

    service = ApplicationService()

    result = service.update_application(
        db=data.db,
        user_id=data.user_id,
        application_id=data.application_id,
        status="interview",
        interview_at_provided=False,
    )

    assert result.interview_at == existing_interview

    # No reminder query or notification creation should occur
    # because interview_at_provided is False.
    data.db.commit.assert_called_once()


def test_missing_application_raises_value_error():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    service = ApplicationService()

    with pytest.raises(ValueError, match="Application not found"):
        service.update_application(
            db=db,
            user_id=uuid4(),
            application_id=uuid4(),
            status="interview",
        )

    db.commit.assert_not_called()


def test_notification_failure_rolls_back_transaction(
    setup_application,
):
    data = setup_application

    interview_at = datetime.now(timezone.utc) + timedelta(days=2)

    with patch(
        "app.jobs.application_service.NotificationService"
    ) as notification_service_class:
        notification_service_class.return_value.create_notification.side_effect = (
            RuntimeError("Simulated notification failure")
        )

        service = ApplicationService()

        with pytest.raises(
            RuntimeError,
            match="Simulated notification failure",
        ):
            service.update_application(
                db=data.db,
                user_id=data.user_id,
                application_id=data.application_id,
                interview_at=interview_at,
                interview_at_provided=True,
            )

    data.db.rollback.assert_called_once()
    data.db.commit.assert_not_called()