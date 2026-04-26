from sqlalchemy.orm import Session
from backend.app.modules.feedback.model import Feedback
import pandas as pd


def get_feedback_df(db: Session, company_id: int) -> pd.DataFrame:
    feedbacks = db.query(Feedback).filter(Feedback.company_id == company_id).all()
    data = [{
        'id': f.id,
        'company_id': f.company_id,
        'product_model_number': f.product_model_number,
        'channel': f.channel,
        'text': f.text,
        'sentiment': f.sentiment,
        'topics': f.topics,
        'email': f.email,
        'mobile': f.mobile,
        'user_id': f.user_id,
        'name': f.name,
        'sentiment_score': f.sentiment_score,
        'likes': f.likes,
        'created_at': f.created_at
    } for f in feedbacks]
    return pd.DataFrame(data)

