import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.jobs.application_model import Application
from app.jobs.model import Job
from app.notifications.service import NotificationService
from app.notifications.model import Notification as NotificationServiceNotification


class ApplicationService:

    def create_application(
        self,
        db: Session,
        user_id: uuid.UUID,
        job_id: uuid.UUID | None,
        status: str,
        applied_at,
        notes: str | None,
        follow_up_at,
    ):
        if job_id:
            job = (
                db.query(Job)
                .filter(Job.id == job_id)
                .first()
            )

            if not job:
                raise ValueError("Job not found")

        application = Application(
            user_id=user_id,
            job_id=job_id,
            status=status,
            applied_at=applied_at,
            notes=notes,
            follow_up_at=follow_up_at,
        )

        db.add(application)
        db.commit()
        db.refresh(application)

        return application

    def get_user_applications(
        self,
        db: Session,
        user_id: uuid.UUID,
    ):
        applications = (
            db.query(Application, Job)
            .outerjoin(
                Job,
                Application.job_id == Job.id,
            )
            .filter(Application.user_id == user_id)
            .order_by(Application.applied_at.desc())
            .all()
        )

        return [
            {
                "id": str(application.id),
                "job_id": (
                    str(application.job_id)
                    if application.job_id
                    else None
                ),
                "title": job.title if job else None,
                "company": job.company if job else None,
                "status": application.status,
                "applied_at": application.applied_at,
                "notes": application.notes,
                "follow_up_at": application.follow_up_at,
                "interview_at": application.interview_at,
            }
            for application, job in applications
        ]

    def get_application(
        self,
        db: Session,
        user_id: uuid.UUID,
        application_id: uuid.UUID,
    ):
        result = (
            db.query(Application, Job)
            .outerjoin(
                Job,
                Application.job_id == Job.id,
            )
            .filter(
                Application.id == application_id,
                Application.user_id == user_id,
            )
            .first()
        )

        if not result:
            raise ValueError("Application not found")

        application, job = result

        return {
            "id": str(application.id),
            "job_id": (
                str(application.job_id)
                if application.job_id
                else None
            ),
            "title": job.title if job else None,
            "company": job.company if job else None,
            "status": application.status,
            "applied_at": application.applied_at,
            "notes": application.notes,
            "follow_up_at": application.follow_up_at,
            "interview_at": application.interview_at,
        }

    def update_application(
        self,
        db: Session,
        user_id: uuid.UUID,
        application_id: uuid.UUID,
        status: str | None = None,
        notes: str | None = None,
        follow_up_at=None,
        interview_at=None,
        interview_at_provided: bool = False,
    ):
        application = (
            db.query(Application)
            .filter(
                Application.id == application_id,
                Application.user_id == user_id,
            )
            .first()
        )

        if not application:
            raise ValueError("Application not found")

        try:
            # Update application fields.
            if status is not None:
                application.status = status

            if notes is not None:
                application.notes = notes

            if follow_up_at is not None:
                application.follow_up_at = follow_up_at

            # Process interview scheduling when the field is provided.
            if interview_at_provided:

                # Cancel existing pending reminders for this application.
                pending_reminders = (
                    db.query(NotificationServiceNotification)
                    .filter(
                        NotificationServiceNotification.application_id
                        == application.id,
                        NotificationServiceNotification.user_id == user_id,
                        NotificationServiceNotification.notification_type
                        == "interview_reminder",
                        NotificationServiceNotification.is_sent.is_(False),
                    )
                    .all()
                )

                for reminder in pending_reminders:
                    db.delete(reminder)

                # Explicit null means the interview has been cancelled.
                if interview_at is None:
                    application.interview_at = None

                else:
                    # Require a timezone-aware interview timestamp.
                    if (
                        interview_at.tzinfo is None
                        or interview_at.utcoffset() is None
                    ):
                        raise ValueError(
                            "Interview date must include a timezone."
                        )

                    application.interview_at = interview_at

                    # Calculate interview and reminder times in UTC.
                    interview_time_utc = interview_at.astimezone(timezone.utc)
                    reminder_at = interview_time_utc - timedelta(hours=24)
                    now = datetime.now(timezone.utc)

                    # Skip reminders for interviews that have already started.
                    if interview_time_utc > now:
                        # If the 24-hour reminder deadline has passed,
                        # schedule the reminder for immediate processing.
                        if reminder_at <= now:
                            reminder_at = now
                        job = None

                        if application.job_id:
                            job = (
                                db.query(Job)
                                .filter(Job.id == application.job_id)
                                .first()
                            )

                        job_title = job.title if job else "your job"
                        company_name = (
                            job.company if job else "the company"
                        )

                        notification_service = NotificationService()

                        notification_service.create_notification(
                            db=db,
                            user_id=user_id,
                            application_id=application.id,
                            title="Interview Reminder",
                            message=(
                                f"Your interview for {job_title} "
                                f"at {company_name} is scheduled for "
                                f"{interview_at.isoformat()}."
                            ),
                            notification_type="interview_reminder",
                            scheduled_at=reminder_at,
                            commit=False,
                        )

            db.commit()
            db.refresh(application)

            return application

        except Exception:
            db.rollback()
            raise

    def delete_application(
        self,
        db: Session,
        user_id: uuid.UUID,
        application_id: uuid.UUID,
    ):
        application = (
            db.query(Application)
            .filter(
                Application.id == application_id,
                Application.user_id == user_id,
            )
            .first()
        )

        if not application:
            raise ValueError("Application not found")

        db.delete(application)
        db.commit()

        return True
    