from sqlalchemy.orm import Session
from backend.models.feedback import Feedback
from backend.schemas.feedback_schema import FeedbackCreate
from typing import List, Union

def get_feedbacks(db: Session, company_id: int):
    return db.query(Feedback).filter(Feedback.company_id == company_id).all()

def create_feedback(db: Session, feedback: Union[FeedbackCreate, dict]):
    # Convert dict to FeedbackCreate if needed
    if isinstance(feedback, dict):
        feedback = FeedbackCreate(**feedback)
    db_feedback = Feedback(**feedback.dict())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def create_feedbacks_bulk(db: Session, feedbacks: List[Union[FeedbackCreate, dict]]):
    db_feedbacks = []
    for feedback in feedbacks:
        if isinstance(feedback, dict):
            feedback = FeedbackCreate(**feedback)
        db_feedbacks.append(Feedback(**feedback.dict()))
    db.add_all(db_feedbacks)
    db.commit()
    for fb in db_feedbacks:
        db.refresh(fb)
    return db_feedbacks
