from sqlalchemy import Column, Integer, String, Text, ForeignKey, PrimaryKeyConstraint
from backend.app.db.base import Base


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        PrimaryKeyConstraint("company_id", "model_number", name="pk_products_company_id_model_number"),
        {"extend_existing": True},
    )
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    model_number = Column(String(100), nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)

