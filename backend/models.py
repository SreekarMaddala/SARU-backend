from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String, index=True)
    channel = Column(String)
    text = Column(Text)
    sentiment = Column(String)
    topics = Column(String)  # Could be JSON, but using String for simplicity
    created_at = Column(DateTime(timezone=True), server_default=func.now())
