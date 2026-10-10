from apscheduler.schedulers.background import BackgroundScheduler

from app.core.database import SessionLocal
from app.notifications.service import NotificationService
from app.notifications.delivery import NotificationDeliveryService


def process_notifications():
    """
    Find due notifications and pass them to the delivery service.
    """

    db = SessionLocal()

    try:
        delivery_service = NotificationDeliveryService()

        due_count = delivery_service.deliver_due_notifications(db)

        if due_count > 0:
            print(
                f"[Notification Scheduler] "
                f"Found {due_count} notification(s) awaiting delivery."
            )

    except Exception as exc:
        db.rollback()
        print(f"[Notification Scheduler] Error: {exc}")

    finally:
        db.close()


scheduler = BackgroundScheduler(timezone="UTC")


def start_scheduler():
    """
    Start the notification scheduler.
    """

    if not scheduler.running:
        scheduler.add_job(
            process_notifications,
            trigger="interval",
            seconds=60,
            id="notification_processor",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )

        scheduler.start()

        print("[Notification Scheduler] Started.")


def stop_scheduler():
    """
    Stop the notification scheduler.
    """

    if scheduler.running:
        scheduler.shutdown(wait=False)

        print("[Notification Scheduler] Stopped.")