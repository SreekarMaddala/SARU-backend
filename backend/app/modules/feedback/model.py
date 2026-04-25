from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.sql import func
from backend.app.db.base import Base


class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    channel = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    sentiment = Column(String, nullable=True)
    topics = Column(String, nullable=True)
    email_or_mobile = Column(String(100), ForeignKey("users.email_or_mobile"), nullable=True)
    name = Column(String(100), nullable=False)
    sentiment_score = Column(Float, nullable=True)
    likes = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

