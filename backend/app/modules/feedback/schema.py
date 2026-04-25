from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class FeedbackBase(BaseModel):
    channel: str
    text: str
    sentiment: Optional[str] = None
    topics: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    name: Optional[str] = None
    sentiment_score: Optional[float] = None
    likes: Optional[int] = None


class FeedbackCreate(FeedbackBase):
    company_id: int
    product_model_number: Optional[str] = None


class FeedbackRead(FeedbackBase):
    id: int
    company_id: int
    product_model_number: Optional[str] = None
    user_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackBulkCreate(BaseModel):
    feedbacks: List[FeedbackCreate]

