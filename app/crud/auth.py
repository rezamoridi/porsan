from core.database import Session
from datetime import datetime
from models.models import UserToken
from models.models import User
from schemas.auth import UserUpdate
from middleware.auth_middleware import AuthService


# Token CRUD Operations


def create_user_token(
    db: Session,
    user_id: int,
    access_token: str,
    refresh_token: str,
    device_info: str,
    ip_address: str,
    access_expires: datetime,
    refresh_expires: datetime
):
    db_token = UserToken(
        user_id=user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        device_info=device_info,
        ip_address=ip_address,
        access_token_expires=access_expires,
        refresh_token_expires=refresh_expires
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def revoke_token(db: Session, refresh_token: str):
    db.query(UserToken)\
      .filter(UserToken.refresh_token == refresh_token)\
      .update({"revoked": True, "revoked_at": datetime.now(datetime.timezone.utc)})
    db.commit()

def get_active_tokens(db: Session, user_id: int):
    return db.query(UserToken)\
             .filter(UserToken.user_id == user_id,
                     UserToken.revoked == False,
                     UserToken.refresh_token_expires > datetime.now(datetime.timezone.utc))\
             .all()


# CRUD Operations
def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def update_user(db: Session, username: str, user_update: UserUpdate):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    
    if 'password' in update_data:
        update_data['hashed_password'] = AuthService.get_password_hash(update_data.pop('password'))
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, username: str):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        return None
    
    db_user.is_active = False  # Soft delete
    db.commit()
    return db_user

