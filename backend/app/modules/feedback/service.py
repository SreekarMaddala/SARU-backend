from sqlalchemy.orm import Session
from backend.app.modules.feedback.model import Feedback
from backend.app.modules.feedback.schema import FeedbackCreate
from backend.app.modules.users.model import User
from typing import List, Union
from textblob import TextBlob
import re


def get_feedbacks(db: Session, company_id: int):
    return db.query(Feedback).filter(Feedback.company_id == company_id).all()


def enrich_feedback_data(text: str) -> dict:
    blob = TextBlob(text)
    sentiment_score = blob.sentiment.polarity
    if sentiment_score > 0.1:
        sentiment = "positive"
    elif sentiment_score < -0.1:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    topics = ", ".join(set(blob.noun_phrases + [word for word, pos in blob.tags if pos in ['NN', 'NNS', 'JJ', 'JJR', 'JJS']][:5]))

    return {
        "sentiment": sentiment,
        "sentiment_score": sentiment_score,
        "topics": topics
    }


def get_or_create_user(db: Session, email_or_mobile: str, name: str = None, company_id: int = None) -> str:
    user = db.query(User).filter(User.email_or_mobile == email_or_mobile).first()
    if user:
        if not user.company_id and company_id:
            user.company_id = company_id
            db.commit()
        if not user.name and name:
            user.name = name
            db.commit()
        return user.email_or_mobile
    else:
        new_user = User(
            email_or_mobile=email_or_mobile,
            name=name,
            company_id=company_id
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user.email_or_mobile


def create_feedback(db: Session, feedback: Union[FeedbackCreate, dict]):
    if isinstance(feedback, dict):
        feedback = FeedbackCreate(**feedback)

    enriched = enrich_feedback_data(feedback.text)
    feedback.sentiment = enriched["sentiment"]
    feedback.sentiment_score = enriched["sentiment_score"]
    feedback.topics = enriched["topics"]

    feedback.email_or_mobile = get_or_create_user(db, feedback.email_or_mobile, feedback.name, feedback.company_id)

    db_feedback = Feedback(**feedback.model_dump())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


def create_feedbacks_bulk(db: Session, feedbacks: List[Union[FeedbackCreate, dict]]):
    db_feedbacks = []
    for feedback in feedbacks:
        if isinstance(feedback, dict):
            feedback = FeedbackCreate(**feedback)
        enriched = enrich_feedback_data(feedback.text)
        feedback.sentiment = enriched["sentiment"]
        feedback.sentiment_score = enriched["sentiment_score"]
        feedback.topics = enriched["topics"]

        feedback.email_or_mobile = get_or_create_user(db, feedback.email_or_mobile, feedback.name, feedback.company_id)

        db_feedbacks.append(Feedback(**feedback.model_dump()))
    db.add_all(db_feedbacks)
    db.commit()
    for fb in db_feedbacks:
        db.refresh(fb)
    return db_feedbacks

