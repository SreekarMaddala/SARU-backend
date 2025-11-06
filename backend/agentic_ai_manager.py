from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.models.feedback import Feedback
from backend.models.ai_insight import AiInsight


class AgenticAIManager:
    """Agentic AI layer that autonomously collects feedback, analyzes it, and stores insights.

    Lifecycle: collect data -> analyze -> store -> repeat periodically (weekly) for continuous learning.
    """

    @staticmethod
    def collect_feedback_data(db: Session, company_id: int, days: int = 7) -> List[Feedback]:
        return (
            db.query(Feedback)
            .filter(Feedback.company_id == company_id)
            .order_by(desc(Feedback.created_at))
            .limit(2000)
            .all()
        )

    @staticmethod
    def generate_ai_summary(feedback_list: List[Feedback]) -> Dict[str, str]:
        if not feedback_list:
            return {"summary": "No new feedback in the selected period.", "themes": ""}

        total = len(feedback_list)
        positives = sum(1 for f in feedback_list if f.sentiment == "positive")
        negatives = sum(1 for f in feedback_list if f.sentiment == "negative")
        neutrals = total - positives - negatives

        # Extract lightweight themes from topics/text
        topics = []
        for f in feedback_list:
            if f.topics:
                topics.extend([t.strip().lower() for t in f.topics.split(",") if t.strip()])
        top_themes = {}
        for t in topics:
            top_themes[t] = top_themes.get(t, 0) + 1
        top_themes_sorted = sorted(top_themes.items(), key=lambda x: x[1], reverse=True)[:10]

        summary = (
            f"Analyzed {total} feedback items. Positive: {positives}, Neutral: {neutrals}, Negative: {negatives}. "
            f"Top recurring themes: {', '.join(t for t, _ in top_themes_sorted) if top_themes_sorted else 'None'}"
        )

        return {"summary": summary, "themes": ", ".join(t for t, _ in top_themes_sorted)}

    @staticmethod
    def suggest_actions(summary: Dict[str, str]) -> str:
        themes = summary.get("themes", "")
        if not themes:
            return (
                "Maintain current service levels. Encourage more feedback to discover actionable patterns."
            )
        recs = [
            "Prioritize fixes for most frequent complaint themes.",
            "Publish a short product update addressing top issues.",
            "Create help articles for recurring support topics.",
            "Monitor sentiment weekly and compare trendlines.",
        ]
        return f"Focus areas: {themes}. Recommendations: " + " ".join(recs)

    @classmethod
    def analyze_and_store(cls, db: Session, company_id: int) -> AiInsight:
        feedback = cls.collect_feedback_data(db, company_id)
        summary = cls.generate_ai_summary(feedback)
        recommendations = cls.suggest_actions(summary)

        insight = AiInsight(
            company_id=company_id,
            summary=summary["summary"],
            recommendations=recommendations,
        )
        db.add(insight)
        db.commit()
        db.refresh(insight)
        return insight


