from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.database import get_db
from backend.auth import get_current_company
from backend.agentic_ai_manager import AgenticAIManager
from backend.models.ai_insight import AiInsight
from backend.schemas.agentic_schema import AiInsight as AiInsightSchema


router = APIRouter(prefix="/agentic", tags=["agentic"])


@router.post("/analyze", response_model=AiInsightSchema)
def trigger_analysis(background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    """Triggers agentic AI analysis in a background task and returns the created insight."""
    insight = AgenticAIManager.analyze_and_store(db, current_company.id)
    return insight


@router.get("/insights", response_model=list[AiInsightSchema])
def get_latest_insights(limit: int = 5, db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    """Returns latest AI-generated insights for the current company."""
    rows = (
        db.query(AiInsight)
        .filter(AiInsight.company_id == current_company.id)
        .order_by(desc(AiInsight.created_at))
        .limit(limit)
        .all()
    )
    return rows


