from database.database import Base
from datetime import datetime, timezone
import enum
from sqlalchemy import Column,Integer,String,Boolean,DateTime,ForeignKey,Enum as SQLEnum
from sqlalchemy.orm import relationship

class Users(Base):
    __tablename__="Users"
    id = Column(Integer,primary_key=True,nullable=False)
    name =Column(String,nullable=False)
    email= Column(String,nullable=False)
    password= Column(String,nullable=False)
    role= Column(String,nullable=False)
    create_date = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

class Events(Base):
    __tablename__="Events"
    id = Column(Integer,primary_key=True,nullable=False)
    org_id = Column(Integer,ForeignKey(Users.id,ondelete="CASCADE"),nullable=False)
    title =Column(String,nullable=False)
    venue= Column(String,nullable=False)
    city= Column(String,nullable=False)
    category= Column(String,nullable=False)
    event_status= Column(String,nullable=False)
    start_at_datetime = Column(DateTime, nullable=False)
    user=relationship("Users")
class TicketType(Base):
    __tablename__="TicketType"
    id = Column(Integer,primary_key=True,nullable=False)
    event_id = Column(Integer,ForeignKey(Events.id,ondelete="CASCADE"),nullable=False)
    name =Column(String,nullable=False)
    price =Column(Integer,nullable=False)
    total_seats =Column(Integer,nullable=False)
    available_seats =Column(Integer,nullable=False)
    events=relationship("Events")
class Booking(Base):
    __tablename__="Booking"
    id = Column(Integer,primary_key=True,nullable=False)
    customer_id = Column(Integer,ForeignKey(Users.id,ondelete="CASCADE"),nullable=False)
    event_id = Column(Integer,ForeignKey(Events.id,ondelete="CASCADE"),nullable=False)
    booking_status =Column(String,nullable=False)
    total_amount =Column(Integer,nullable=False)
    expire_at = Column(DateTime, nullable=False)
    create_date = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    customer=relationship("Users")
    events=relationship("Events")

class PaymentStatus(str, enum.Enum):
    pending = "pending"
    success = "success"
    failed = "failed"

class Payment(Base):
    __tablename__ = "Payment"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("Booking.id"))
    amount = Column(Integer, nullable=False)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.pending)
    paid_at =Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

class BookingItem(Base):
    __tablename__ = "BookingItem"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("Booking.id"))
    ticket_type_id = Column(Integer, ForeignKey("TicketType.id"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False)