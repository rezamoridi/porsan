from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from core.database import get_db
from middleware.auth_middleware import get_current_user, get_admin, get_super_admin
from schemas.event import EventBase, EventCreate, EventDB, EventImageBase, EventImageCreate, EventImageDB, EventUpdate
from models.models import Event, EventImage, User
from services.uploader import BucketObj_2
from uuid import uuid4
from random import randint, choice

router = APIRouter(
    prefix="/api/admin/event"
)


# Event Management Routes
@router.post("/create", response_model=EventCreate, 
             dependencies=[Depends(get_admin)])
async def create_event(
    *,
    db: Session = Depends(get_db),
    event_in: EventBase,
    current_admin: User = Depends(get_current_user)
):
    """Create a new event (admin only)"""
    event_db = Event(**event_in.model_dump())
    db.add(event_db)
    db.commit()
    db.refresh(event_db)
    return event_db



router = APIRouter()



router = APIRouter()

@router.get("/get_all/", 
            #response_model=List[dict], dependencies=[Depends(get_admin)]
            )
async def list_events(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None
):
    """List all events with optional filters and add dynamic fields"""
    query = db.query(Event)
    
    if start_date:
        query = query.filter(Event.start_date >= start_date)
    if end_date:
        query = query.filter(Event.end_date <= end_date)
    if search:
        query = query.filter(
            Event.subject.ilike(f"%{search}%") |
            Event.description.ilike(f"%{search}%")
        )
    
    events = query.offset(skip).limit(limit).all()
    
    # Add static values dynamically
    response = []
    for event in events:
        event_data = {
            "id": event.id,
            "subject": event.subject,
            "description": event.description,
            "text": event.text,
            "start_date": event.start_date,
            "end_date": event.end_date,
            "code": event.code,
            "created_at": event.created_at,
            "teacher_name": choice(["Dr. John Doe", "Prof. Alice Smith", "Dr. Robert Brown"]),
            "user_rate": randint(1, 5),
            "progress": randint(0, 100),
            "image_url": event.images[0].image_id if event.images else None  # Fetch first image if available
        }
        response.append(event_data)
    
    return response




@router.get("/get/{event_id}", response_model=EventDB,
            dependencies=[Depends(get_admin)])
async def get_event(
    event_id: int = Path(...),
    db: Session = Depends(get_db)
):
    """Get a specific event by ID"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.put("/update/{event_id}", response_model=EventDB,
            dependencies=[Depends(get_admin)])
async def update_event(
    *,
    db: Session = Depends(get_db),
    event_id: int,
    event_in: EventUpdate,
    #current_admin: User = Depends(get_admin)
):
    """Update an event (admin only)"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    update_data = event_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@router.delete("delete/{event_id}",
               dependencies=[Depends(get_admin)])
async def delete_event(
    *,
    db: Session = Depends(get_db),
    event_id: int,
    #current_admin: User = Depends(get_admin)
):
    """Delete an event (admin only)"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(event)
    db.commit()
    return {"message": "Event deleted successfully"}

# Event Image Routes
@router.post("add/{event_id}/images",
              response_model=None,
             dependencies=[Depends(get_admin)])
async def upload_event_image(
    *,
    db: Session = Depends(get_db),
    event_id: int,
    files: List[UploadFile] = File(...),
    current_admin: User = Depends(get_admin)
):
    """Upload an image for an event (admin only)"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Save file and get image ID
    save_names = [f"{event_id}_{str(uuid4())}" for _ in range(len(files))]
    images = BucketObj_2(files= files, save_names=save_names, destination="events", format_="jpg")
    images.upload_images()
    links = images.generate_perma_links()
    
    # Create image record
    for link in links:
        event_image = EventImage(
            image_id=link,
            event_id=event_id
        )
        db.add(event_image)
        db.commit()
        db.refresh(event_image)
    return {"event_id": event_id, "new_images": len(links)}

@router.delete("/{event_id}/images/{image_id}",
               dependencies=[Depends(get_admin)])
async def delete_event_image(
    *,
    db: Session = Depends(get_db),
    event_id: int,
    image_id: int,
    current_admin: User = Depends(get_current_user)
):
    """Delete an event image (admin only)"""
    image = db.query(EventImage).filter(
        EventImage.id == image_id,
        EventImage.event_id == event_id
    ).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    db.delete(image)
    db.commit()
    return {"message": "Image deleted successfully"}

