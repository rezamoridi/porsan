from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from middleware.auth_middleware import get_admin, get_current_user
from core.database import get_db, Session
from models.models import User, UserImage
from services.uploader import BucketObj_2
from uuid import uuid4
from sqlalchemy.orm import joinedload
# User Models
class AdminBase(BaseModel):
    username: str = Field(..., min_length=4, max_length=20)
    passowrd: str = Field(..., min_length=8, max_length=100)
    name: Optional[str] = Field(None, max_length=50)
    sid: str = Field(..., pattern=r"\d{11}")
    lname: str = Field(..., min_length=3, max_length=20)
    fa_name: str = Field(..., min_length=3, max_length=20)
    phone_number: str = Field(..., min_length=11, max_length=11)
    birth_date: datetime


class AdminUpdate(AdminBase):
    status: bool
    degree: str
    university_id: int = Field(le=1)
    department_id: int = Field(le=1)
    birth_city: str = Field(min_length=3, max_length=25)
    major: str = Field(min_length=3,max_length=30)
    degree: str = Field(min_length=3, max_length=20)



class AdminDB(AdminUpdate):
    role_id: int
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateAvatar(BaseModel):
    avatar_url: str
    message: str


# Auth Router
router = APIRouter(
    prefix="/api/admin"
)





@router.get(
        path="/get_me"
)
async def get_me(
    admin = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    admin_db = db.query(User).filter(User.id == admin["user_id"]).first()
    if not admin_db:
        raise HTTPException(status_code=401, detail="Auth neededm, check credentials")
    return {"user_id": admin_db.id, "username": admin_db.username}


@router.put(
        "/update", 
        response_model=AdminDB
)
async def update_current_admin(
    user_update: AdminUpdate,
    db: Session =  Depends(get_db), 
    admin= Depends(get_current_user)
):
    admin_db = db.query(User).filter(User.id == admin["user_id"]).first()
    for key, value in user_update.model_dump().items():
        setattr(admin_db, key, value)

    db.commit()
    return admin_db


@router.post("/admin/upload-image", response_model=UpdateAvatar)
async def upload_admin_image(
    file: UploadFile = File(...),
    admin = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    admin_db = db.query(User).filter(User.id == admin["user_id"]).first()
    if not admin_db:
        raise HTTPException(status_code=404, detail="Admin not found!")
    random = uuid4()
    new_avatar = BucketObj_2(files=[file], save_names=[f"{random}"], destination="users")
    new_avatar.upload_images()
    link = new_avatar.generate_perma_links()
    if not link:
        return HTTPException(status_code=400, detail="avatar upload faild!")

    user_image = db.query(UserImage).filter(UserImage.user_id == admin_db.id).first()
    if not user_image:
        new_image = UserImage(user_id = admin_db.id, avatar_url = link[0])
        db.add(new_image)
    else:
        user_image.avatar_url = link[0]
        db.add(user_image)
    db.commit()
    return {"avatar_url": link[0], "message": f"Admin {admin["user_id"]} image uploaded successfully"}



@router.post(
        "/logout"
)
async def admin_logout(
    db: Session=Depends(get_db),
    admin = Depends(get_current_user)
):
    admin_db = db.query(User).filter(User.id == admin["user_id"]).first()
    if not admin_db or admin_db.access_token == None:
        raise HTTPException(status_code=404, detail="Admin not found! or logged out")
    admin_db.access_token = None
    admin_db.refresh_token = None
    db.commit() 
    return {"message": "User logged out successfully"}




@router.get("/get_users/")
async def get_users(db: Session = Depends(get_db)):
    db_users = db.query(User).options(joinedload(User.avatar)).all()  # Join the UserImage (avatar) table
    
    users = [
        {
            "id": user.id,
            "name": user.name,
            "image": user.avatar.avatar_url if user.avatar else None,  # Get avatar_url from the UserImage model
            "role": user.role.name if user.role else None  # Get role name
        }
        for user in db_users
    ]
    
    return users