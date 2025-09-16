from pydantic import BaseModel
from datetime import datetime

class CompanyBase(BaseModel):
    name: str
    email: str

class CompanyCreate(CompanyBase):
    password: str

class Company(CompanyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CompanyLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None
