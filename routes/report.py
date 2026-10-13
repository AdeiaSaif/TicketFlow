from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import database, models
from auth2 import get_current_user

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/events/{id}/sales", status_code=status.HTTP_200_OK)
def get_event_sales(id: int, db: Session = Depends(database.get_db), user: int = Depends(get_current_user)):
    organizer = db.query(models.Users).filter(models.Users.id == user.id, models.Users.role == "organizer").first()
    if not organizer:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only organizers are allowed to view sales reports.")
    event = db.query(models.Events).filter(models.Events.id == id, models.Events.org_id == user.id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found or you do not have permission for this event.")
    confirmed_bookings = db.query(models.Booking).filter(models.Booking.event_id == event.id, models.Booking.booking_status == "confirmed").all()
    total_revenue = sum(b.total_amount for b in confirmed_bookings)
    total_sales_count = len(confirmed_bookings)
    return { "event_id": event.id, "event_title": event.title,"total_confirmed_bookings": total_sales_count,"total_revenue": total_revenue, "bookings": confirmed_bookings}

@router.get("/organizer/summary", status_code=status.HTTP_200_OK)
def get_organizer_summary(db: Session = Depends(database.get_db), user: int = Depends(get_current_user)):
    organizer = db.query(models.Users).filter(models.Users.id == user.id, models.Users.role == "organizer").first()
    if not organizer:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only organizers are allowed to view summary reports.")
    events = db.query(models.Events).filter(models.Events.org_id == user.id).all()
    event_ids = [e.id for e in events]
    total_events_created = len(events)
    if event_ids:
        confirmed_bookings = db.query(models.Booking).filter(models.Booking.event_id.in_(event_ids), models.Booking.booking_status == "confirmed").all()
        overall_revenue = sum(b.total_amount for b in confirmed_bookings)
        total_tickets_sold = len(confirmed_bookings)
    else:
        overall_revenue = 0
        total_tickets_sold = 0
    return {
        "organizer_id": user.id,
        "organizer_name": user.name,
        "total_events": total_events_created,
        "total_tickets_sold": total_tickets_sold,
        "overall_revenue": overall_revenue,
        "events": [{"id": e.id, "title": e.title} for e in events]
    }