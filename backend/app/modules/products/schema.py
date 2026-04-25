from pydantic import BaseModel, ConfigDict
from typing import Optional


class ProductBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    name: str
    description: Optional[str] = None
    model_number: str
    company_id: int


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    class Config:
        from_attributes = True


class ProductUpdate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    name: Optional[str] = None
    description: Optional[str] = None
    model_number: Optional[str] = None

