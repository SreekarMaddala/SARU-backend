from pydantic import BaseModel
from datetime import datetime

class FeedbackBase(BaseModel):
    company_id: str
    channel: str
    text: str
    sentiment: str
    topics: str

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
