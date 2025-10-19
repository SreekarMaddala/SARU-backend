from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.sql import func
from ..database import Base
class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    channel = Column(String, nullable=False)               # e.g., twitter, email, phone
    text = Column(Text, nullable=False)                    # feedback content
    sentiment = Column(String, nullable=True)              # positive / negative / neutral
    topics = Column(String, nullable=True)                 # tags or categories
    email_or_mobile = Column(String(100), ForeignKey("users.email_or_mobile"), nullable=True)  # user identifier
    name = Column(String(100), nullable=False)              # name of user (from user table or input)
    sentiment_score = Column(Float, nullable=True)         # numeric sentiment value
    likes = Column(Integer, nullable=True)                 # number of likes (for social media)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
