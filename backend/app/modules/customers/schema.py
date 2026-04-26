from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TopProductItem(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_number: str
    name: Optional[str] = None
    feedback_count: int


class CustomerProfileResponse(BaseModel):
    id: int
    name: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    created_at: datetime
    total_feedback_count: int
    average_sentiment: Optional[float] = None
    last_feedback_at: Optional[datetime] = None
    top_products: list[TopProductItem]
