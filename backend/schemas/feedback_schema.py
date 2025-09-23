from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


# ------------------- RAW FEEDBACK -------------------
class FeedbackBase(BaseModel):
    channel: str                   # e.g., "twitter", "email", "phone"
    text: str                      # feedback message
    sentiment: Optional[str] = None  # positive / negative / neutral
    topics: Optional[str] = None     # topic tags or categories
    likes: Optional[int] = None      # likes/engagement count (only for twitter)
    user_ref: Optional[str] = None   # twitter handle / email / phone number


class FeedbackCreate(FeedbackBase):
    company_id: int  # filled from token internally


class Feedback(FeedbackBase):
    id: int
    company_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackBulkCreate(BaseModel):
    feedbacks: List[FeedbackCreate]


# ------------------- FEEDBACK SUMMARY (for analysis) -------------------
class FeedbackSummaryBase(BaseModel):
    company_id: int
    channel: str
    date: datetime                  # aggregated per day
    sentiment_positive: int = 0
    sentiment_negative: int = 0
    sentiment_neutral: int = 0
    top_topics: Optional[str] = None  # top N topics stored as JSON/CSV


class FeedbackSummary(FeedbackSummaryBase):
    id: int

    class Config:
        from_attributes = True
