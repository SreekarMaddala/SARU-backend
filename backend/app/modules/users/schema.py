from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    email: str | None = None
    mobile: str | None = None
    name: str | None = None


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

