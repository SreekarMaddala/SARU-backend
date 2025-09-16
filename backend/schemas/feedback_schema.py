from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class FeedbackBase(BaseModel):
    channel: str
    text: str
    sentiment: Optional[str] = None
    topics: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    company_id: int  # Keep for internal use, but will be set from token

class Feedback(FeedbackBase):
    id: int
    company_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class FeedbackBulkCreate(BaseModel):
    feedbacks: List[FeedbackCreate]
