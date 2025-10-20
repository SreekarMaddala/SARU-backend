from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.sql import func
from ..database import Base

class User(Base):
    __tablename__ = "users"
    email_or_mobile = Column(String(100), primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
