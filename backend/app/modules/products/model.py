from sqlalchemy import Column, Integer, String, Text, ForeignKey, PrimaryKeyConstraint, Sequence
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from backend.app.db.base import Base


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        PrimaryKeyConstraint("company_id", "model_number", name="pk_products_company_id_model_number"),
        {"extend_existing": True},
    )
    id = Column(
        Integer,
        Sequence("products_api_id_seq"),
        unique=True,
        index=True,
        nullable=False,
    )
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    model_number = Column(String(100), nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

