from sqlalchemy.orm import Session
from backend.models.feedback import Feedback
from backend.models.user import User
from backend.schemas.feedback_schema import FeedbackCreate
from typing import List, Union
from textblob import TextBlob
import re

def get_feedbacks(db: Session, company_id: int):
    return db.query(Feedback).filter(Feedback.company_id == company_id).all()

def enrich_feedback_data(text: str) -> dict:
    """
    Enrich feedback data with sentiment and topics.
    """
    blob = TextBlob(text)
    sentiment_score = blob.sentiment.polarity
    if sentiment_score > 0.1:
        sentiment = "positive"
    elif sentiment_score < -0.1:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    # Extract topics: simple keyword extraction (nouns and adjectives)
    topics = ", ".join(set(blob.noun_phrases + [word for word, pos in blob.tags if pos in ['NN', 'NNS', 'JJ', 'JJR', 'JJS']][:5]))  # limit to 5 topics

    return {
        "sentiment": sentiment,
        "sentiment_score": sentiment_score,
        "topics": topics
    }

def get_or_create_user(db: Session, email_or_mobile: str, name: str = None) -> int:
    """
    Get existing user or create new one.
    """
    user = db.query(User).filter(User.email_or_mobile == email_or_mobile).first()
    if user:
        if name and not user.name:
            user.name = name
            db.commit()
        return user.id
    else:
        new_user = User(email_or_mobile=email_or_mobile, name=name)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user.id

def create_feedback(db: Session, feedback: Union[FeedbackCreate, dict]):
    # Convert dict to FeedbackCreate if needed
    if isinstance(feedback, dict):
        feedback = FeedbackCreate(**feedback)

    # Enrich data
    enriched = enrich_feedback_data(feedback.text)
    feedback.sentiment = enriched["sentiment"]
    feedback.sentiment_score = enriched["sentiment_score"]
    feedback.topics = enriched["topics"]

    # Handle user
    if feedback.email_or_mobile:
        feedback.user_id = get_or_create_user(db, feedback.email_or_mobile, feedback.name)
    else:
        feedback.user_id = None

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
        # Enrich data
        enriched = enrich_feedback_data(feedback.text)
        feedback.sentiment = enriched["sentiment"]
        feedback.sentiment_score = enriched["sentiment_score"]
        feedback.topics = enriched["topics"]

        # Handle user
        if feedback.email_or_mobile:
            feedback.user_id = get_or_create_user(db, feedback.email_or_mobile, feedback.name)
        else:
            feedback.user_id = None

        db_feedbacks.append(Feedback(**feedback.dict()))
    db.add_all(db_feedbacks)
    db.commit()
    for fb in db_feedbacks:
        db.refresh(fb)
    return db_feedbacks
