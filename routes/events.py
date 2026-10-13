from fastapi import APIRouter,Depends,HTTPException, status
from database.database import get_db
from auth2 import get_current_user
from schemas import Events,Events_Update
from sqlalchemy.orm import Session
from typing import Optional
import database.models as models
router=APIRouter(prefix="/events")

@router.post("/create")
def create_events(events:Events,db:Session=Depends(get_db),user:int=Depends(get_current_user)):
    check_user=db.query(models.Users).filter(models.Users.id==user.id).first()
    check_role= check_user.role=="organizer"
    if check_role:
        new_event=models.Events(**events.dict())
        new_event.org_id=user.id
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        return {"event_title":events.title,"organizer_id":user}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create events."
        )

@router.put("/update/{id}")
def update_event(event:Events_Update,id:int,db:Session=Depends(get_db),user:int=Depends(get_current_user)):
    event_query=db.query(models.Events).filter(models.Events.org_id==user.id , id==models.Events.id)
    check_event=event_query.first()
    if check_event:
        if event.start_at_datetime:
            db.query(models.Booking).filter(models.Booking.event_id==id).update({models.Booking.expire_at: event.start_at_datetime},synchronize_session=False)
            db.commit()
        update_data=event.model_dump(exclude_unset=True)
        event_query.update(update_data)
        db.commit()
        db.refresh(check_event)
        return {"event_title":event.title}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update events."
            )

@router.delete("/delete/{id}")
def update_event(id:int,db:Session=Depends(get_db),user:int=Depends(get_current_user)):
    event_query=db.query(models.Events).filter(models.Events.org_id==user.id, id==models.Events.id)
    check_event=event_query.first()
    if check_event:
        event_query.delete(synchronize_session=False)
        db.commit()
        return {"Message":"event deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete events."
            )


@router.get("/mine")
def create_events(db:Session=Depends(get_db),user:int=Depends(get_current_user)):
    my_events=db.query(models.Events).filter(models.Events.org_id==user.id).all()
    return my_events
@router.get("/search")
def create_events(city:Optional[str]="",category:Optional[str]="",db:Session=Depends(get_db)):
    my_events=db.query(models.Events).filter(models.Events.city.contains(city)).filter(models.Events.category.contains(category)).all()
    return my_events
@router.get("/{id}")
def create_events(id:int,db:Session=Depends(get_db)):
    my_events=db.query(models.Events).filter(models.Events.id==id).all()
    return my_events
