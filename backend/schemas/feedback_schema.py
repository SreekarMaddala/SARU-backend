from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


# ------------------- RAW FEEDBACK -------------------
class FeedbackBase(BaseModel):
    channel: str
    text: str
    sentiment: Optional[str] = None
    topics: Optional[str] = None
    user_id: Optional[str] = None
    name: Optional[str] = None
    email_or_mobile: Optional[str] = None
    sentiment_score: Optional[float] = None


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
