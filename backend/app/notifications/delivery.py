from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from html import escape

from sqlalchemy.orm import Session

from app.models.user import User
from app.jobs.application_model import Application
from app.jobs.model import Job
from app.notifications.model import Notification
from app.notifications.email_service import EmailService




class NotificationDeliveryService:
    """
    Sends due scheduled notifications through email.
    """

    def deliver_due_notifications(self, db: Session) -> int:
        """
        Send due interview reminders through Resend.

        Mark a notification as sent only after Resend accepts
        the email request.
        """

        now = datetime.now(timezone.utc)

        due_notifications = (
            db.query(Notification)
            .filter(
                Notification.is_sent.is_(False),
                Notification.scheduled_at.is_not(None),
                Notification.scheduled_at <= now,
                Notification.notification_type == "interview_reminder",
            )
            .order_by(Notification.scheduled_at.asc())
            .all()
        )

        if not due_notifications:
            return 0

        email_service = EmailService()
        successful_count = 0

        for notification in due_notifications:
            try:
                user = (
                    db.query(User)
                    .filter(User.id == notification.user_id)
                    .first()
                )

                if user is None or not user.email:
                    print(
                        "[Notification Delivery] "
                        f"No email address for notification "
                        f"{notification.id}"
                    )
                    continue

                # Find the application associated with this reminder.
                application = None

                if notification.application_id is not None:
                    application = (
                        db.query(Application)
                        .filter(
                            Application.id == notification.application_id,
                            Application.user_id == user.id,
                        )
                        .first()
                    )

                job = None

                if application and application.job_id:
                    job = (
                        db.query(Job)
                        .filter(Job.id == application.job_id)
                        .first()
                    )

                # Prepare personalized email details.
                candidate_name = escape(
                    (user.full_name or "Candidate").strip()
                )

                job_title = (
                    job.title
                    if job
                    else notification.title or "Interview Reminder"
                )

                company_name = (
                    job.company
                    if job
                    else "Please check your application tracker"
                )

                job_title = escape(job_title)
                company_name = escape(company_name)

                # Convert the interview time to Indian Standard Time.
                interview_datetime = (
                    application.interview_at
                    if application
                    else None
                )

                if interview_datetime:
                    if interview_datetime.tzinfo is None:
                        interview_datetime = interview_datetime.replace(
                            tzinfo=timezone.utc
                        )

                    interview_datetime = interview_datetime.astimezone(
                        ZoneInfo("Asia/Kolkata")
                    )

                    formatted_date = interview_datetime.strftime(
                        "%A, %d %B %Y"
                    )
                    formatted_time = interview_datetime.strftime(
                        "%I:%M %p IST"
                    )
                else:
                    formatted_date = "Please check your application tracker"
                    formatted_time = "Please confirm the interview time"

                subject = f"Interview Reminder: {job_title}"

                html_content = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport"
                          content="width=device-width, initial-scale=1.0">
                    <title>Interview Reminder</title>
                </head>
                <body style="
                    margin: 0;
                    padding: 0;
                    background-color: #f4f7fb;
                    font-family: Arial, Helvetica, sans-serif;
                    color: #263238;
                ">
                    <div style="
                        max-width: 600px;
                        margin: 30px auto;
                        background-color: #ffffff;
                        border-radius: 12px;
                        overflow: hidden;
                        border: 1px solid #e5e7eb;
                    ">
                        <div style="
                            background-color: #1d4ed8;
                            padding: 28px 24px;
                            text-align: center;
                            color: #ffffff;
                        ">
                            <h1 style="margin: 0; font-size: 25px;">
                                CareerForge AI
                            </h1>
                            <p style="margin: 10px 0 0;">
                                Your career journey, supported.
                            </p>
                        </div>

                        <div style="padding: 28px 24px;">
                            <h2 style="
                                margin-top: 0;
                                color: #1d4ed8;
                            ">
                                Interview Reminder
                            </h2>

                            <p>Hello {candidate_name},</p>

                            <p>
                                This is a friendly reminder about your
                                upcoming interview. Here are the details
                                available in your application tracker.
                            </p>

                            <div style="
                                background-color: #eff6ff;
                                border-left: 4px solid #2563eb;
                                padding: 18px;
                                margin: 22px 0;
                                border-radius: 6px;
                            ">
                                <p style="margin: 0 0 12px;">
                                    <strong>Position:</strong>
                                    {job_title}
                                </p>

                                <p style="margin: 0 0 12px;">
                                    <strong>Company:</strong>
                                    {company_name}
                                </p>

                                <p style="margin: 0 0 12px;">
                                    <strong>Date:</strong>
                                    {escape(formatted_date)}
                                </p>

                                <p style="margin: 0;">
                                    <strong>Time:</strong>
                                    {escape(formatted_time)}
                                </p>
                            </div>

                            <h3>Before your interview</h3>

                            <ul style="line-height: 1.8; padding-left: 22px;">
                                <li>Review the job description.</li>
                                <li>Revise relevant technical concepts.</li>
                                <li>Prepare examples of your projects.</li>
                                <li>Confirm the meeting link or venue.</li>
                            </ul>

                            <p>
                                We wish you the very best for your interview.
                                Stay confident and give it your best!
                            </p>

                            <p style="margin-top: 28px;">
                                Best wishes,<br>
                                <strong>Team CareerForge AI</strong>
                            </p>
                        </div>

                        <div style="
                            background-color: #f8fafc;
                            padding: 16px 24px;
                            text-align: center;
                            font-size: 12px;
                            color: #64748b;
                        ">
                            This is an automated reminder from CareerForge AI.
                        </div>
                    </div>
                </body>
                </html>
                """

                text_content = (
                    "Interview Reminder\n\n"
                    f"Hello {user.full_name},\n\n"
                    "This is a reminder about your upcoming interview.\n\n"
                    f"Position: {job.title if job else notification.title or 'Interview Reminder'}\n"
                    f"Company: {job.company if job else 'Please check your application tracker'}\n"
                    f"Date: {formatted_date}\n"
                    f"Time: {formatted_time}\n\n"
                    "Before your interview:\n"
                    "- Review the job description.\n"
                    "- Revise relevant technical concepts.\n"
                    "- Prepare examples of your projects.\n"
                    "- Confirm the meeting link or venue.\n\n"
                    "We wish you the very best!\n\n"
                    "Team CareerForge AI"
                )

                email_id = email_service.send_email(
                    to_email=user.email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                )

                notification.is_sent = True
                db.commit()

                successful_count += 1

                print(
                    "[Notification Delivery] Email accepted by "
                    f"Resend for notification {notification.id}. "
                    f"Email ID: {email_id}"
                )

            except Exception as exc:
                db.rollback()

                print(
                    "[Notification Delivery] Failed to send "
                    f"notification {notification.id}: "
                    f"{type(exc).__name__}: {exc}"
                )

        return successful_count