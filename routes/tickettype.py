from fastapi import APIRouter,Depends,status,HTTPException
import schemas
from sqlalchemy.orm import session
from database import models
from database import database
from auth2 import get_current_user

router=APIRouter(prefix="/tickettype")

@router.post("/ticket-type")
def create_ticket(ticket:schemas.TicketType,db:session=Depends(database.get_db),organizer:int=Depends(get_current_user)):
    check=db.query(models.Events).filter(models.Events.id==ticket.event_id, models.Events.org_id==organizer.id).first()
    if check:
        new_ticket=models.TicketType(**ticket.dict())
        new_ticket.available_seats = ticket.total_seats
        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)
        return new_ticket
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create tickets for this event or the event was not found.")
@router.put("/update/{id}")
def update_ticket(id: int, ticket: schemas.TicketType_update, db: session = Depends(database.get_db), organizer: int = Depends(get_current_user)):
    ticket_query = db.query(models.TicketType).filter(models.TicketType.id == id, models.Events.org_id == organizer.id)
    db_ticket = ticket_query.first()
    if not db_ticket:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Ticket type not found or you do not have permission to update it.")
    update_data = ticket.model_dump(exclude_unset=True)
    if "total_seats" in update_data:
        new_available = db_ticket.available_seats + (update_data["total_seats"] - db_ticket.total_seats)
        if new_available < 0:
            raise HTTPException(status_code=400, detail="New total seats cannot be less than the number of seats already booked.")
        update_data["available_seats"] = new_available
    ticket_query.update(update_data)
    db.commit()
    db.refresh(db_ticket)
    return {"message": "Updated ticket record successfully","updated_ticket": db_ticket}



@router.delete("/delete/{id}")
def delete_ticket(id:int,db: session = Depends(database.get_db), organizer: int = Depends(get_current_user)):
    ticket_query = db.query(models.TicketType).filter(models.TicketType.id == id, models.Events.org_id == organizer.id)
    db_ticket = ticket_query.first()
    if not db_ticket:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Ticket type not found or you do not have permission to update it.")
    else:
        ticket_query.delete(synchronize_session=False)
        db.commit()
        return {"Message":"Ticket Type deleted"}

@router.get("/events/{event_id}/ticket-types")
def get_event_ticket_types(event_id: int, db: session = Depends(database.get_db),org:int=Depends(get_current_user)):
    event = db.query(models.Events).filter(models.Events.id == event_id,org.id==models.Events.org_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    tickets = db.query(models.TicketType).filter(models.TicketType.event_id == event_id).all()
    return {"ticket_types": tickets}