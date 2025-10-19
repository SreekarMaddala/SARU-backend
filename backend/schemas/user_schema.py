from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    email_or_mobile: str
    name: str | None = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    created_at: datetime

    class Config:
        from_attributes = True
