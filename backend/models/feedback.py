from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from backend.database import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    channel = Column(String, nullable=False)           # twitter, email, phone, etc.
    text = Column(Text, nullable=False)                # feedback content
    sentiment = Column(String, nullable=True)          # positive / negative / neutral
    topics = Column(String, nullable=True)             # tags or categories
    likes = Column(Integer, default=0)                 # likes/engagement (only for twitter)
    user_ref = Column(String, nullable=True)           # twitter handle / email / phone
    created_at = Column(DateTime(timezone=True), server_default=func.now())
