from fastapi import APIRouter, Depends
from database.models import Events, TicketType
from database.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import String, cast, and_
from typing import Optional

router = APIRouter()

@router.get("/event_search")
def Event_Search(
    city: Optional[str] = None,
    date: Optional[str] = None,
    category: Optional[str] = None,
    venue: Optional[str] = None,
    title: Optional[str] = None,
    price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Events, TicketType).join(
        TicketType,
        Events.id == TicketType.event_id
    )

    filters = []

    if price is not None:
        filters.append(TicketType.price <= price)

    if date:
        filters.append(
            cast(Events.start_at_datetime, String).like(f"%{date}%")
        )

    if city:
        filters.append(Events.city.ilike(f"%{city}%"))

    if category:
        filters.append(Events.category.ilike(f"%{category}%"))

    if venue:
        filters.append(Events.venue.ilike(f"%{venue}%"))

    if title:
        filters.append(Events.title.ilike(f"%{title}%"))

    if filters:
        query = query.filter(and_(*filters))

    data = query.all()

    return {
        "result": [
            {
                "event": {
                    "id": event.id,
                    "title": event.title,
                    "city": event.city,
                    "category": event.category,
                    "venue": event.venue,
                    "start_at_datetime": str(event.start_at_datetime)
                },
                "ticket": {
                    "id": ticket.id,
                    "price": ticket.price
                }
            }
            for event, ticket in data
        ]
    }