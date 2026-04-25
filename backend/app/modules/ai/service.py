from sqlalchemy.orm import Session
from backend.app.modules.ai.manager import AgenticAIManager
from backend.app.modules.ai.model import AiInsight


def trigger_analysis(db: Session, company_id: int) -> AiInsight:
    return AgenticAIManager.analyze_and_store(db, company_id)


def get_latest_insights(db: Session, company_id: int, limit: int = 5):
    from sqlalchemy import desc
    return (
        db.query(AiInsight)
        .filter(AiInsight.company_id == company_id)
        .order_by(desc(AiInsight.created_at))
        .limit(limit)
        .all()
    )

