from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.core.security import get_current_company
from backend.app.modules.analytics import service as analytics_service
from backend.app.modules.analytics.schema import CustomerRetentionResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/sentiment")
def sentiment_analysis(db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    return analytics_service.sentiment_analysis_service(db, current_company.id)


@router.get("/topics")
def topic_modeling(db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    return analytics_service.topic_modeling_service(db, current_company.id)


@router.get("/channels")
def channel_analysis(db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    return analytics_service.channel_analysis_service(db, current_company.id)


@router.get("/users")
def user_behavior_analysis(db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    return analytics_service.user_behavior_analysis_service(db, current_company.id)


@router.get("/company-performance")
def company_performance_analysis(db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    return analytics_service.company_performance_analysis_service(db, current_company.id)


@router.get("/products")
def product_feedback_analysis(db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    return analytics_service.product_feedback_analysis_service(db, current_company.id)


@router.get("/temporal")
def temporal_analysis(db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    return analytics_service.temporal_analysis_service(db, current_company.id)


@router.get("/customer-retention", response_model=CustomerRetentionResponse)
def customer_retention(db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    return analytics_service.customer_retention_service(db, current_company.id)

