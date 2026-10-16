from enum import Enum
from pydantic import BaseModel,EmailStr
from datetime import datetime
from typing import Optional,List
from pydantic_settings import BaseSettings
class User(BaseModel):
    
    name:str
    email: EmailStr
    password:str
    role:str

class Setting(BaseSettings):
    SECRET_KEY:str
    ALGORITHM:str
    DATABASE_URL:str
    REDIS_URL: str
    MISTRAL_API_KEY:str
    class Config:
        env_file=".env"
settings = Setting()

class TokenData(BaseModel):
    id:int

class Events(BaseModel):
    
    title :str
    venue:str
    city:str
    category:str
    event_status:str
    start_at_datetime : datetime
class Events_Update(BaseModel):
    title: Optional[str] = None
    venue: Optional[str] = None
    city: Optional[str] = None
    category: Optional[str] = None
    event_status: Optional[str] = None
    start_at_datetime: Optional[datetime] = None
class TicketType(BaseModel):
    id :int
    event_id:int
    name :str   
    price :int  
    total_seats :int 
class TicketType_update(BaseModel):
    id :Optional[int] =None
    event_id:Optional[int]=None
    name :Optional[str]=None
    price :Optional[int] =None
    total_seats :Optional[int]=None
    available_seats :Optional[int]=None
class Booking(BaseModel):
    event_id :int
    booking_status :str
    total_amount :int
class Booking_update(BaseModel):
    event_id :Optional[int]=None
    booking_status :Optional[str]=None
    total_amount :Optional[int]=None


class PaymentStatusEnum(str, Enum):
    pending = "pending"
    success = "success"
    failed = "failed"

class PaymentCreate(BaseModel):
    booking_id: int
    amount: int

class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    amount: int
    status: PaymentStatusEnum
    paid_at: datetime

    class Config:
        from_attributes = True

class BookingItemCreate(BaseModel):
    ticket_type_id: int
    quantity: int

class BookingItemResponse(BaseModel):
    id: int
    ticket_type_id: int
    quantity: int
    unit_price: int

    class Config:
        from_attributes = True

class BookingItemCreate(BaseModel):
    ticket_type_id: int
    quantity: int

class BookingCreate(BaseModel):
    event_id: int
    items: List[BookingItemCreate]
class AskRequest(BaseModel):
    question: str
class AskResponse(BaseModel):
    answer: str
    sources: list[int]
