from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, ForeignKey, DateTime, 
    Index, CheckConstraint, UniqueConstraint, JSON, Table
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Association Tables
user_interests = Table(
    'user_interests', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('interest_id', Integer, ForeignKey('interests.id', ondelete='CASCADE'), primary_key=True)
)

survey_tags = Table(
    'survey_tags', Base.metadata,
    Column('survey_id', Integer, ForeignKey('surveys.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False, default=1)
    token_version = Column(Integer, default=0)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    role = relationship("Role", backref="users")
    surveys = relationship("Survey", back_populates="user")
    interests = relationship("Interest", secondary=user_interests)
    notifications = relationship("Notification", back_populates="recipient")

class UserToken(Base):
    __tablename__ = 'user_tokens'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    access_token = Column(String(512), nullable=False)
    refresh_token = Column(String(512), unique=True, nullable=False)
    device_info = Column(Text)
    ip_address = Column(String(45))
    access_token_expires = Column(DateTime, nullable=False)
    refresh_token_expires = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())

class Survey(Base):
    __tablename__ = 'surveys'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(20), 
                   CheckConstraint("status IN ('draft', 'active', 'closed')"),
                   default='draft')
    is_featured = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="surveys")
    questions = relationship("Question", back_populates="survey")
    responses = relationship("SurveyResponse", back_populates="survey")
    tags = relationship("Tag", secondary=survey_tags)
    settings = relationship("SurveySetting", uselist=False, back_populates="survey")

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey('surveys.id', ondelete='CASCADE'))
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), 
                          CheckConstraint("question_type IN ('multiple_choice', 'text', 'rating', 'dropdown')"),
                          nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    survey = relationship("Survey", back_populates="questions")
    choices = relationship("Choice", back_populates="question")
    responses = relationship("Response", back_populates="question")

class Choice(Base):
    __tablename__ = 'choices'
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'))
    choice_text = Column(Text, nullable=False)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    
    question = relationship("Question", back_populates="choices")

class SurveyResponse(Base):
    __tablename__ = 'survey_responses'
    id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey('surveys.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    created_at = Column(DateTime, default=func.now())
    
    survey = relationship("Survey", back_populates="responses")
    user = relationship("User")
    responses = relationship("Response", back_populates="survey_response")
    response_metadata = relationship("ResponseMetadata", uselist=False, back_populates="response_group")

class Response(Base):
    __tablename__ = 'responses'
    id = Column(Integer, primary_key=True)
    survey_response_id = Column(Integer, ForeignKey('survey_responses.id', ondelete='CASCADE'))
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    time_taken_seconds = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    
    survey_response = relationship("SurveyResponse", back_populates="responses")
    question = relationship("Question", back_populates="responses")
    user = relationship("User")
    text_response = relationship("TextResponse", uselist=False, back_populates="response")
    choice_responses = relationship("ChoiceResponse", back_populates="response")

class TextResponse(Base):
    __tablename__ = 'text_responses'
    response_id = Column(Integer, ForeignKey('responses.id', ondelete='CASCADE'), primary_key=True)
    text_response = Column(Text, nullable=False)
    
    response = relationship("Response", back_populates="text_response")

class ChoiceResponse(Base):
    __tablename__ = 'choice_responses'
    response_id = Column(Integer, ForeignKey('responses.id', ondelete='CASCADE'), primary_key=True)
    choice_id = Column(Integer, ForeignKey('choices.id', ondelete='CASCADE'), primary_key=True)
    
    response = relationship("Response", back_populates="choice_responses")
    choice = relationship("Choice")

class ResponseMetadata(Base):
    __tablename__ = 'response_metadata'
    survey_response_id = Column(Integer, ForeignKey('survey_responses.id'), primary_key=True)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    geo_location = Column(Text)
    submitted_at = Column(DateTime, default=func.now())
    
    response_group = relationship("SurveyResponse", back_populates="response_metadata")

class Interest(Base):
    __tablename__ = 'interests'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    recipient_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    message = Column(Text, nullable=False)
    notification_type = Column(String(50))
    related_survey_id = Column(Integer, ForeignKey('surveys.id', ondelete='SET NULL'))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    recipient = relationship("User", back_populates="notifications")
    related_survey = relationship("Survey")

class SurveySetting(Base):
    __tablename__ = 'survey_settings'
    id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey('surveys.id', ondelete='CASCADE'))
    settings = Column(JSONB, default={
        "allow_anonymous": True,
        "response_limit": None,
        "require_login": False
    })
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    survey = relationship("Survey", back_populates="settings")

class SurveyAnalytics(Base):
    __tablename__ = 'survey_analytics'
    __table_args__ = {'info': dict(is_materialized_view=True)}
    
    survey_id = Column(Integer, primary_key=True)
    total_participants = Column(Integer)
    total_answers = Column(Integer)
    avg_response_time = Column(Integer)
    
    @classmethod
    def refresh(cls, session):
        session.execute('REFRESH MATERIALIZED VIEW survey_analytics')