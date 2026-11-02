from fastapi import APIRouter,Depends,HTTPException,status
from database import database,models
from sqlalchemy.orm import session
from auth2 import get_current_user
from schemas import Booking,Booking_update
from datetime import timedelta, datetime
router=APIRouter(prefix="/booking")


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import database, models
from auth2 import get_current_user
from schemas import BookingCreate

router = APIRouter(prefix="/booking", tags=["Bookings"])


def expire_pending_bookings(db: Session):
    try:
        expired_bookings = (
            db.query(models.Booking)
            .filter(
                models.Booking.booking_status == "pending",
                models.Booking.expire_at <= datetime.utcnow()
            )
            .order_by(models.Booking.id)
            .with_for_update(skip_locked=True)
            .all()
        )

        for booking in expired_bookings:

            booking_items = (
                db.query(models.BookingItem)
                .filter(
                    models.BookingItem.booking_id == booking.id
                )
                .all()
            )

            ticket_quantities = {}

            for item in booking_items:
                ticket_id = item.ticket_type_id

                ticket_quantities[ticket_id] = (
                    ticket_quantities.get(ticket_id, 0) + item.quantity
                )

            for ticket_id, quantity in sorted(ticket_quantities.items()):

                ticket_type = (
                    db.query(models.TicketType)
                    .filter(models.TicketType.id == ticket_id)
                    .with_for_update()
                    .first()
                )

                if ticket_type:
                    ticket_type.available_seats += quantity

            booking.booking_status = "expired"

        db.commit()

        return len(expired_bookings)

    except Exception:
        db.rollback()
        raise


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_booking( booking_data: BookingCreate, user: int = Depends(get_current_user),db: Session = Depends(database.get_db)):
    customer = db.query(models.Users).filter( models.Users.id == user.id,models.Users.role == "customer" ).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only customers are allowed to create bookings.")

    event = db.query(models.Events).filter(models.Events.id == booking_data.event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    ticket_quantities = {}

    for item in booking_data.items:
        ticket_id = item.ticket_type_id
        ticket_quantities[ticket_id] = ( ticket_quantities.get(ticket_id, 0) + item.quantity )

    total_amount = 0
    ticket_validations = []

    try:
        for ticket_id, quantity in sorted(ticket_quantities.items()):
            ticket_type = (db.query(models.TicketType).filter(models.TicketType.id == ticket_id,models.TicketType.event_id == event.id).with_for_update().first())
            if not ticket_type:
                raise HTTPException( status_code=404,detail=f"Ticket type {ticket_id} not found")

            if ticket_type.available_seats < quantity:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not enough seats available for '{ticket_type.name}'. Available: {ticket_type.available_seats}")

            total_amount += ticket_type.price * quantity
            ticket_validations.append((ticket_type, quantity))

        new_booking = models.Booking(customer_id=user.id, event_id=event.id,  booking_status="pending",  total_amount=total_amount,expire_at=datetime.utcnow() + timedelta(minutes=15))
        db.add(new_booking)
        db.flush()

        for ticket_type, quantity in ticket_validations:
            ticket_type.available_seats -= quantity
            booking_item = models.BookingItem( booking_id=new_booking.id,ticket_type_id=ticket_type.id,quantity=quantity,unit_price=ticket_type.price)
            db.add(booking_item)

        db.commit()
        db.refresh(new_booking)
        return {"message": "Booking created successfully and seats reserved.","booking_id": new_booking.id,"total_amount": new_booking.total_amount,"booking_status": new_booking.booking_status}

    except Exception:
        db.rollback()
        raise



@router.get("/")
def get_customer_bookings(db: session = Depends(database.get_db), user: int = Depends(get_current_user)):
    bookings = db.query(models.Booking).filter(models.Booking.customer_id == user.id).all()
    return bookings
@router.get("/{id}")
def get_booking_detail(id: int, db: session = Depends(database.get_db), user: int = Depends(get_current_user)):
    booking = db.query(models.Booking).filter(models.Booking.id == id,models.Booking.customer_id == user.id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking



@router.post("/{id}/cancel", status_code=status.HTTP_200_OK)
def cancel_booking(id: int, db: session = Depends(database.get_db), user: int = Depends(get_current_user)):
    booking = db.query(models.Booking).filter( models.Booking.id == id, models.Booking.customer_id == user.id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.booking_status == "cancelled":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Booking is already cancelled.")
    booking.booking_status = "cancelled"
    booking_items = db.query(models.BookingItem).filter(models.BookingItem.booking_id == booking.id).all()
    for item in booking_items:
        ticket_type = db.query(models.TicketType).filter(models.TicketType.id == item.ticket_type_id).first()
        if ticket_type:
            ticket_type.available_seats += item.quantity 
    db.commit()
    db.refresh(booking)
    return {"message": "Booking cancelled successfully and seats released.","booking_id": booking.id,"booking_status": booking.booking_status}