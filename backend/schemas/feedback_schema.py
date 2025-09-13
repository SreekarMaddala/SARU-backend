from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class FeedbackBase(BaseModel):
    company_id: str
    channel: str
    text: str
    sentiment: Optional[str] = None
    topics: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class FeedbackBulkCreate(BaseModel):
    feedbacks: List[FeedbackCreate]
