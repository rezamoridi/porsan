from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os
load_dotenv()

DB_USER_NAME = os.getenv("DB_USER_NAME") 
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST_NAME = os.getenv("DB_HOST_NAME")
DB_NAME = os.getenv("DB_NAME")


DATABASE_URL = f"postgresql+psycopg2://{DB_USER_NAME}:{DB_PASSWORD}@{DB_HOST_NAME}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autoflush= False, autocommit= False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
