from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models.models import User
from core.database import Session, get_db
from middleware.auth_middleware import get_current_user, get_admin, AuthService, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(
    prefix="/api/auth/admin"
)

@router.post(path="/login",
             response_model=None)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: Session = Depends(get_db)
):
    # Get user from database
    admin_db = db.query(User).filter(User.username == form_data.username).first()
    
    # Validate credentials
    if not admin_db or not AuthService.verify_password(form_data.password, admin_db.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Get device info
    
    # Create tokens

    tokens = AuthService.create_tokens(admin_db.id, admin_db.role_id)

    
    # Store token in database
    admin_db.access_token = tokens["access_token"]
    admin_db.refresh_token = tokens["refresh_token"]
    admin_db.last_login = datetime.now()


    db.commit()


    return {
        "access_token": tokens["access_token"],
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }