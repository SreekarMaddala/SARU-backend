from pydantic import BaseModel
from datetime import datetime


class AiInsightBase(BaseModel):
    summary: str
    recommendations: str


class AiInsightCreate(AiInsightBase):
    company_id: int


class AiInsight(AiInsightBase):
    id: int
    company_id: int
    created_at: datetime

    class Config:
        from_attributes = True


