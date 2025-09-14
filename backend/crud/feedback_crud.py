from sqlalchemy.orm import Session
from backend.models.feedback import Feedback
from backend.schemas.feedback_schema import FeedbackCreate
from typing import List

def get_feedbacks(db: Session):
    return db.query(Feedback).all()

def create_feedback(db: Session, feedback: FeedbackCreate):
    db_feedback = Feedback(**feedback.dict())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def create_feedbacks_bulk(db: Session, feedbacks: List[FeedbackCreate]):
    db_feedbacks = [Feedback(**feedback.dict()) for feedback in feedbacks]
    db.add_all(db_feedbacks)
    db.commit()
    for fb in db_feedbacks:
        db.refresh(fb)
    return db_feedbacks
