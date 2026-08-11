
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, JSON, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    assessments = relationship("Assessment", back_populates="owner")

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    answers = Column(JSON)
    prediction = Column(String) # "Menopausal" or "Premenopausal"
    probability = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="assessments")
