from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, ForeignKeyConstraint
from sqlalchemy.sql import func
from backend.app.db.base import Base


class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    product_model_number = Column(String(100), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    channel = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    sentiment = Column(String, nullable=True)
    topics = Column(String, nullable=True)
    name = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    mobile = Column(String(50), nullable=True, index=True)
    sentiment_score = Column(Float, nullable=True)
    likes = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        ForeignKeyConstraint(
            ['company_id', 'product_model_number'],
            ['products.company_id', 'products.model_number'],
            ondelete='CASCADE',
            name='fk_feedback_product'
        ),
    )

