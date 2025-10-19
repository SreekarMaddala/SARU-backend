from sqlalchemy import Column, Integer, String, Text
from ..database import Base

class Product(Base):
    __tablename__ = "products"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)