from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from core.database import get_db, Session
from models.models import User
import random
from middleware.auth_middleware import AuthService
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

class SignupUser(BaseModel):
    username: str
    name: str
    lname: str
    phone_number: str
    id_number: str
    avatar: Optional[str] = None  # You can use a URL for avatar or leave it as None

    class Config:
        orm_mode = True  # This will allow Pydantic to work with SQLAlchemy models


# Auth Router
router = APIRouter(
    prefix="/api/user"
)
from models.models import Role

class SignupModel(BaseModel):
    name: str
    lname: str
    phone_number: str
    id_number: str
    avatar: str

from datetime import timezone
def generate_username(name: str, lname: str) -> str:
    return f"{name.lower()}.{lname.lower()}.{random.randint(100, 999)}"


@router.post("/register")
async def user_register(user: SignupModel, db: Session = Depends(get_db)):
    # Check if the ID number is already taken
    if db.query(User).filter(User.id_number == user.id_number).first():
        raise HTTPException(status_code=409, detail="Duplicated code melli")



    # Generate a random email
    email = f"{user.name.lower()}.{user.lname.lower()}@example.com"
    
    # Generate a username from the name and lname
    username = generate_username(user.name, user.lname)

    # Generate a password (this is a placeholder, you should hash it properly in a real implementation)


    # Create the user object
    new_user = User(
        username=username,
        password=AuthService.get_password_hash(f'{user.id_number}'),
        name=user.name,
        lname=user.lname,
        fa_name=user.name,  # Assuming fa_name is the same as name, adjust as needed
        id_number=user.id_number,
        phone_number=user.phone_number,
        sid = "11111111111",
        role_id=1,
        avatar=None,  # Avatar is added if provided
        created_at=datetime.now(timezone.utc),
    )

    # Add user to the session and commit
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "user_id": new_user.id}

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
