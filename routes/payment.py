from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import database, models
from auth2 import get_current_user
from schemas import Booking, Booking_update, PaymentResponse 

router=APIRouter(prefix='/payment')

@router.post("/{id}/pay", status_code=status.HTTP_200_OK)
def pay_booking(id: int, db: Session = Depends(database.get_db), user: int = Depends(get_current_user)):
    booking = db.query(models.Booking).filter(models.Booking.id == id, models.Booking.customer_id == user.id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.booking_status in ["confirmed", "paid"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Booking is already paid and confirmed.")
    booking.booking_status = "confirmed"
    new_payment = models.Payment(booking_id=booking.id,amount=booking.total_amount,status=models.PaymentStatus.success)
    db.add(new_payment)
    db.commit()
    db.refresh(booking)
    return {"message": "Payment successful! Booking confirmed.","booking_id": booking.id,"booking_status": booking.booking_status,"amount_paid": booking.total_amount}