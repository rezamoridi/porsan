from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates



templates = Jinja2Templates(directory="app/templates")

router = APIRouter(
    prefix="/admin/p"
)


@router.get("/login")
async def login_page(
    request: Request
):
    return templates.TemplateResponse(
        "login.html",
        {"request":request}
    )

@router.get("/dashboard")
async def login_page(
    request: Request
):
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request":request}
    )