from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime

class EventImageBase(BaseModel):
    image_id: str

class EventImageCreate(EventImageBase):
    pass

class EventImageDB(EventImageBase):
    event_id: int
    new_images: int

    class Config:
        from_attributes = True

class EventBase(BaseModel):
    subject: str = Field(min_length=3, max_length=20)
    description: Optional[str] = Field(min_length=3, max_length=50)
    text: Optional[str] = Field(max_length=300)
    start_date: datetime
    end_date: datetime
    code: Optional[str] = Field(max_length=20)

class EventCreate(EventBase):
    created_at: datetime

class EventUpdate(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    text: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    code: Optional[str] = None

class EventDB(EventBase):
    id: int
    created_at: datetime
    images: List[EventImageDB] = []

    class Config:
        from_attributes = True