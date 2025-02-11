from fastapi import HTTPException, status
from core.database import Session
from datetime import datetime
from models.models import User
from middleware.auth_middleware import AuthService


# Token CRUD Operations





# CRUD Operations
def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# CRUD Operations
def get_user_by_id(db: Session, id: int):
    return db.query(User).filter(User.id == id).first()

def check_unique(db: Session, username: str, email: str):
    name_check = db.query(User).filter(User.username == username).first()
    email_check = db.query(User).filter(User.email == email).first()
    if name_check or email_check:
        return False
    return True


def delete_user(db: Session, username: str):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        return None
    
    db_user.is_active = False  # Soft delete
    db.commit()
    return db_user

