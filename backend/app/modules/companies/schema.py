from pydantic import BaseModel
from datetime import datetime


class CompanyBase(BaseModel):
    name: str
    email: str


class CompanyCreate(CompanyBase):
    password: str


class CompanyRead(CompanyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CompanyLogin(BaseModel):
    email: str
    password: str

