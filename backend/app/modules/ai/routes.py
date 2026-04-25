from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.core.security import get_current_company
from backend.app.modules.ai import service as ai_service
from backend.app.modules.ai.schema import AiInsightRead

router = APIRouter(prefix="/agentic", tags=["agentic"])


@router.post("/analyze", response_model=AiInsightRead)
def trigger_analysis(background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    insight = ai_service.trigger_analysis(db, current_company.id)
    return insight


@router.get("/insights", response_model=list[AiInsightRead])
def get_latest_insights(limit: int = 5, db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    rows = ai_service.get_latest_insights(db, current_company.id, limit)
    return rows

