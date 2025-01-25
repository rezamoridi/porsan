from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timezone

# Import your existing components
from middleware.auth_middleware import  AuthService, jwt, Request,  ACCESS_TOKEN_EXPIRE_MINUTES, auth_middleware, get_current_user
from core.database import get_db, Session
from crud.auth import get_user, update_user, delete_user, create_user_token
from models.models import User  # Your User model
from schemas.auth import (  # Your existing schemas
    responses,
    UserCreate,
    UserUpdate,
    UserResponse,
    MessageResponse,
    ErrorResponse,
    TokenResponse
)

router = APIRouter(
    prefix="/user",
    responses={404: {"model": ErrorResponse, "description": "Not found"}}
)



# Auth Endpoints with CRUD
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses=responses
)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    # Check existing user
    if get_user(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": 409, "detail": "Username already exists"}
        )
    
    # Create new user
    hashed_password = AuthService.get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=True,
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Get user from database
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # Validate credentials
    if not user or not AuthService.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Get device info
    device_info = request.headers.get("User-Agent", "Unknown")
    ip_address = request.client.host if request.client else "0.0.0.0"
    
    # Create tokens
    tokens = AuthService.create_tokens(user.id)
    
    # Store token in database
    create_user_token(
        db=db,
        user_id=user.id,
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        device_info=device_info,
        ip_address=ip_address,
        access_expires=tokens["access_expires"],
        refresh_expires=tokens["refresh_expires"]
    )
    
    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    
    # Set refresh token in HTTP-only cookie
    response = Response(content="Login successful")
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        expires=tokens["refresh_expires"],  # Ensure this is a UTC datetime
        httponly=True,
        secure=True,
        samesite="Lax"
    )
    
    return {
        "access_token": tokens["access_token"],
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }



@router.get(
    "/users/me",
    response_model=UserResponse,
    responses={401: {"description": "Unauthorized"}}
)
async def read_current_user(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.patch(
    "/users/me",
    response_model=UserResponse,
    responses={
        400: {"description": "Invalid input"},
        401: {"description": "Unauthorized"}
    }
)
async def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated_user = update_user(db, current_user.username, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": 400, "detail": "Update failed"}
        )
    return updated_user

@router.delete(
    "/users/me",
    response_model=MessageResponse,
    responses={401: {"description": "Unauthorized"}}
)
async def delete_current_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delete_user(db, current_user.username)
    return {"message": "Account deactivated successfully"}

@router.post(
    "/refresh",
    response_model=TokenResponse,
    responses={401: {"description": "Invalid refresh token"}}
)
async def refresh_token(
    request: Request,
    db: Session = Depends(get_db)
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": 401, "detail": "Missing refresh token"}
        )

    try:
        payload = AuthService.decode_token(refresh_token)
        user = get_user(db, payload.sub)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": 401, "detail": "Invalid user"}
            )
        
        new_access_token = AuthService.create_access_token(user.username)
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": 1800
        }
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": 401, "detail": "Refresh token expired"}
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": 401, "detail": "Invalid refresh token"}
        )

@router.post(
    "/logout",
    response_model=MessageResponse,
    responses={401: {"description": "Unauthorized"}}
)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user)
):
    response.delete_cookie("refresh_token")
    return {"message": "Successfully logged out"}

