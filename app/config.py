import logging
from os import path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from models.models import Base
from core.database import engine, SessionLocal
from pydantic_settings import BaseSettings
from services.services import initialize_super_admin






logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



import routers.auth
import routers.event_admin
import routers.user
import routers.admin
import routers.admin_pannel


app = FastAPI()
Base.metadata.create_all(engine)


templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

origins = [
    'localhost:8000/auth/login',
    '127.0.0.1:8000',
    'http://localhost:8000/auth/login',
    'http://127.0.0.1:8000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Replace "*" with the allowed origins
    allow_credentials= True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router= routers.auth.router, tags=["Auth"])
app.include_router(router= routers.admin.router, tags=["Admin"])
app.include_router(router= routers.event_admin.router ,tags=["Admin-Event"])
app.include_router(router= routers.user.router, tags=["User"])
app.include_router(router= routers.admin_pannel.router, tags=["Admin Pannel"])

@app.on_event("startup")
async def startup_event():
    """
    FastAPI startup event to initialize super admin
    """
    logger.info("Starting application...")
    try:
        db = SessionLocal()
        await initialize_super_admin(db)
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
    finally:
        db.close()