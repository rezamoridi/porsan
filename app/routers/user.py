from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from core.database import get_db, Session
from models.models import User
# User Models
class UserBase(BaseModel):
    username: str = Field(..., min_length=4, max_length=20)
    password: str = Field(..., min_length=8, max_length=100)
    name: Optional[str] = Field(None, max_length=50)
    sid: str = Field(..., min_length=11, max_length=11)
    lname: str = Field(..., min_length=3, max_length=20)
    fa_name: str = Field(..., min_length=3, max_length=20)
    phone_number: str = Field(..., pattern=r"^09[\d]{9}$")
    birth_date: datetime
    id_number: str = Field(..., pattern=r"^[\d]{10}$")
    university_id: int = Field(1, ge=1)
    department_id: int = Field(1, ge=1)
    major: str = Field(description="رشته")
    degree: str = Field(description="مدرک")
    address: str
    birth_city: str



class UserCreate(UserBase):
    id: int
    created_at: datetime
    status: bool = Field(True)
    role_id: int

class UserUpdate(BaseModel):
    id_number: int = Field(..., ge=1)
    university_id: int = Field(1, ge=1)
    department_id: int = Field(1, ge=1)
    major: str = Field(description="رشته")
    degree: str = Field(description="مدرک")



class UserDB(UserUpdate):
    id: int
    created_at: datetime
    role_id: int = Field(1)
    last_login: datetime
    class Config:
        from_attributes = True

# Auth Router
router = APIRouter(
    prefix="/api/user"
)

@router.post("/register", response_model=UserCreate)
def register(user: UserBase, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException (status_code=409, detail="username already exists")
    new_user = user.model_dump()
    db_user = User(**new_user)
    db_user.role_id = 1
    db.add(db_user)
    db.commit()

    return db_user


@router.post("/login")
def login(email: EmailStr, password: str):
    return {"message": "User logged in successfully"}

@router.put("/update", response_model=UserDB)
def update_user(user_update: UserUpdate, user_id: int ):
    return UserDB(id=user_id, email="test@example.com", full_name=user_update.full_name, created_at=datetime.utcnow())

@router.post("/logout")
def logout():
    return {"message": "User logged out successfully"}

@router.post("/upload-profile")
def upload_profile(file: UploadFile = File(...)):
    return {"filename": file.filename, "message": "Profile picture uploaded successfully"}

@router.post("/join-event/{event_id}")
def join_event(event_id: int, user_id: int):
    return {"message": f"User {user_id} joined event {event_id}"}

@router.post("/leave-event/{event_id}")
def leave_event(event_id: int, user_id: int):
    return {"message": f"User {user_id} left event {event_id}"}

@router.get("/request-resume/{user_id}")
def request_resume(user_id: int):
    return {"message": f"Resume request received for user {user_id}"}
