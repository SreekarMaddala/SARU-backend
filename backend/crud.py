from sqlalchemy.orm import Session
from models import Feedback
from schemas import FeedbackCreate

def get_feedbacks(db: Session):
    return db.query(Feedback).all()

def create_feedback(db: Session, feedback: FeedbackCreate):
    db_feedback = Feedback(**feedback.dict())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback
