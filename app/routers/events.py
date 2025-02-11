from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from core.database import get_db, Session
from models.models import User

router = APIRouter(
    prefix="/api/event"
)


