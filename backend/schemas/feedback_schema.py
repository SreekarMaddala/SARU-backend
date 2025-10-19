from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


# ------------------- RAW FEEDBACK -------------------
class FeedbackBase(BaseModel):
    channel: str
    text: str
    sentiment: Optional[str] = None
    topics: Optional[str] = None
    user_id: Optional[int] = None
    name: str
    email_or_mobile: str
    sentiment_score: Optional[float] = None
    user_ref: Optional[str] = None
    likes: Optional[int] = None


class FeedbackCreate(FeedbackBase):
    company_id: int


class Feedback(FeedbackBase):
    id: int
    company_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ------------------- BULK CREATE -------------------
class FeedbackBulkCreate(BaseModel):
    feedbacks: List[FeedbackCreate]
