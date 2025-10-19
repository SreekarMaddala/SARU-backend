from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


# ------------------- RAW FEEDBACK -------------------
class FeedbackBase(BaseModel):
    channel: str
    text: str
    sentiment: Optional[str] = None
    topics: Optional[str] = None
    email_or_mobile: str
    name: str
    sentiment_score: Optional[float] = None
    likes: Optional[int] = None


class FeedbackCreate(FeedbackBase):
    company_id: int
    product_id: int | None = None


class Feedback(FeedbackBase):
    id: int
    company_id: int
    product_id: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True


# ------------------- BULK CREATE -------------------
class FeedbackBulkCreate(BaseModel):
    feedbacks: List[FeedbackCreate]
