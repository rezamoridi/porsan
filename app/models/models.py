from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, ForeignKey, DateTime, 
    Index, CheckConstraint, UniqueConstraint, JSON, Table,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()



class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String(20), nullable=False)
    lname = Column(String(20), nullable=False)
    fa_name = Column(String(20), nullable=False)
    id_number = Column(String(10), nullable=False)
    sid = Column(String(11), nullable=False)
    university_id = Column(Integer, ForeignKey('universities.id'))
    department_id = Column(Integer, ForeignKey('departments.id'))
    major = Column(String)
    birth_date = Column(DateTime)
    role_id = Column(Integer, ForeignKey('roles.id'))
    access_token = Column(Text)
    refresh_token = Column(Text)
    last_login = Column(DateTime)
    birth_city = Column(String)
    degree = Column(String)
    phone_number = Column(String(11), CheckConstraint("phone_number LIKE '0%'"), nullable=False)
    address = Column(String(100))
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    status = Column(Boolean, default=True)
    
    university = relationship("University")
    department = relationship("Department")
    role = relationship("Role")
    events = relationship("Event", secondary="user_events", back_populates="users", overlaps="users")
    avatar = relationship("UserImage", uselist=False, back_populates="user")

class Event(Base):
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True)
    subject = Column(Text)
    description = Column(Text)
    text = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    code = Column(String)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    images = relationship("EventImage", back_populates="event")
    users = relationship("User", secondary="user_events", back_populates="events", overlaps="events")

class University(Base):
    __tablename__ = 'universities'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

class Department(Base):
    __tablename__ = 'departments'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

class Major(Base):
    __tablename__ = 'majors'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    desc = Column(Text)

class UserEvents(Base):
    __tablename__ = 'user_events'
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"), primary_key=True)

class UserImage(Base):
    __tablename__ = 'user_images'
    
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    avatar_url = Column(String, nullable=False)
    
    user = relationship("User", back_populates="avatar")

class EventImage(Base):
    __tablename__ = 'event_images'
    
    id = Column(Integer, primary_key=True)
    image_id = Column(String, nullable=False)
    event_id = Column(Integer, ForeignKey('events.id'))
    
    event = relationship("Event", back_populates="images")