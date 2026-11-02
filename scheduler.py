from apscheduler.schedulers.background import BackgroundScheduler
from database.database import SessionLocal
from routes.booking import expire_pending_bookings


def run_booking_expiry():
    db = SessionLocal()

    try:
        expired_count = expire_pending_bookings(db)
        print(f"Expired bookings processed: {expired_count}")
    except Exception as e:
        print(f"Booking expiry error: {e}")
    finally:
        db.close()


scheduler = BackgroundScheduler(timezone="UTC")

scheduler.add_job(
    run_booking_expiry,
    trigger="interval",
    minutes=1,
    id="booking_expiry",
    max_instances=1,
    coalesce=True
)


def start_scheduler():
    if not scheduler.running:
        scheduler.start()


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()