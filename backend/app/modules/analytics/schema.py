from pydantic import BaseModel


class CustomerRetentionSummary(BaseModel):
    retained_customers: int
    churned_customers: int


class CustomerRetentionPeriod(BaseModel):
    period: str
    retention_rate: float
    churn_rate: float
    retained_customers: int
    new_customers: int


class CustomerRetentionResponse(BaseModel):
    summary: CustomerRetentionSummary
    retention_over_time: list[CustomerRetentionPeriod]
