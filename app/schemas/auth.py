# app/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, Union, Dict
from enum import Enum

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"

class UserBase(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        example="john_doe",
        description="Unique username (3-50 characters, no spaces)"
    )
    email: EmailStr = Field(
        ...,
        example="user@example.com",
        description="Valid email address"
    )

class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        example="SecurePass123!",
        description="Password with at least 8 characters, 1 uppercase, 1 number"
    )

    @validator('username')
    def validate_username(cls, v):
        if ' ' in v:
            raise ValueError("Username cannot contain spaces")
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(
        None,
        example="new.email@example.com",
        description="New email address"
    )
    current_password: Optional[str] = Field(
        None,
        min_length=8,
        example="CurrentPass123!",
        description="Current password for verification"
    )
    new_password: Optional[str] = Field(
        None,
        min_length=8,
        example="NewSecurePass123!",
        description="New password (same requirements as registration)"
    )

    @validator('new_password')
    def validate_new_password(cls, v, values):
        if v and not values.get('current_password'):
            raise ValueError("Current password is required to change password")
        return v

class UserResponse(UserBase):
    is_active: bool = Field(..., example=True, description="Account status")
    created_at: datetime = Field(..., example="2023-01-01T00:00:00Z")
    updated_at: datetime = Field(..., example="2023-01-01T00:00:00Z")

    class Config:
        orm_mode = True

class TokenBase(BaseModel):
    token_type: str = Field(..., example="bearer")
    expires_in: int = Field(..., example=1800, description="Expiration in seconds")

class TokenPair(TokenBase):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")

class TokenPayload(BaseModel):
    sub: str = Field(..., description="Subject (username)")
    type: TokenType = Field(..., description="Token type")
    exp: int = Field(..., description="Expiration timestamp")

class LoginRequest(BaseModel):
    username: str = Field(..., example="john_doe")
    password: str = Field(..., example="SecurePass123!")

class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="Valid refresh token")


class ErrorDetail(BaseModel):
    code: int = Field(..., example=400, description="HTTP status code")
    message: str = Field(..., example="Validation error", description="Short error message")
    details: Optional[Union[str, Dict[str, str]]] = Field(
        None, example="Detailed information about the error", description="Optional additional details"
    )


class HTTPErrorResponse(BaseModel):
    error: ErrorDetail

    class Config:
        schema_extra = {
            "example": {
                "error": {
                    "code": 400,
                    "message": "Validation error",
                    "details": {"field": "This field is required"}
                }
            }
        }


class ValidationErrorResponse(HTTPErrorResponse):
    error: ErrorDetail = Field(..., example={
        "code": 422,
        "message": "Validation Error",
        "details": {"username": "Must be unique"}
    })


class ConflictErrorResponse(HTTPErrorResponse):
    error: ErrorDetail = Field(..., example={
        "code": 409,
        "message": "Conflict",
        "details": "Username already exists"
    })

# Add these to your existing auth schemas

class TokenResponse(BaseModel):
    access_token: str = Field(
        ...,
        description="JWT access token for authentication"
    )
    token_type: str = Field(
        default="bearer",
        example="bearer",
        description="Type of token"
    )
    expires_in: int = Field(
        ...,
        example=1800,
        description="Expiration time in seconds"
    )

    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }

class ErrorResponse(BaseModel):
    detail: str = Field(
        ...,
        example="Authentication failed",
        description="Error message"
    )
    code: int = Field(
        ...,
        example=401,
        description="HTTP status code"
    )

    class Config:
        schema_extra = {
            "example": {
                "detail": "Invalid credentials",
                "code": 401
            }
        }


class MessageResponse(BaseModel):
    message: str = Field(..., example="Success message")

# Response models for OpenAPI documentation
responses = {
    201: {"description": "Created", "model": UserResponse},
    400: {"description": "Bad Request", "model": ValidationErrorResponse},
    409: {"description": "Conflict", "model": ConflictErrorResponse},
    422: {"description": "Validation Error", "model": ValidationErrorResponse},
}