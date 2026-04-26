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


def _normalize_email(v: str | None) -> str | None:
    if v is None:
        return None
    v = str(v).strip()
    return v.lower() if v else None


def _normalize_mobile(v: str | None) -> str | None:
    if v is None:
        return None
    v = str(v).strip()
    return v if v else None


def get_or_create_user_id(
    db: Session,
    *,
    email: str | None,
    mobile: str | None,
    name: str | None = None,
    company_id: int | None = None,
) -> int:
    """
    Match priority:
    - if email exists: match by email
    - elif mobile exists: match by mobile
    Create if not found.
    Prevent duplicates via DB unique indexes + retry on conflicts.
    """
    email_n = _normalize_email(email)
    mobile_n = _normalize_mobile(mobile)

    if not email_n and not mobile_n:
        raise ValueError("Either email or mobile must be provided")

    user = None
    if email_n:
        user = db.query(User).filter(User.email == email_n).first()
    if user is None and mobile_n:
        user = db.query(User).filter(User.mobile == mobile_n).first()

    if user is not None:
        changed = False
        if company_id and not user.company_id:
            user.company_id = company_id
            changed = True
        if name and not user.name:
            user.name = name
            changed = True
        if email_n and not user.email:
            user.email = email_n
            changed = True
        if mobile_n and not user.mobile:
            user.mobile = mobile_n
            changed = True
        if changed:
            db.commit()
            db.refresh(user)
        return user.id

    # Create new user; handle race (unique constraint) by retrying lookup.
    new_user = User(email=email_n, mobile=mobile_n, name=name, company_id=company_id)
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
        return new_user.id
    except Exception:
        db.rollback()
        # Someone else may have inserted the same email/mobile.
        if email_n:
            user = db.query(User).filter(User.email == email_n).first()
        if user is None and mobile_n:
            user = db.query(User).filter(User.mobile == mobile_n).first()
        if user is None:
            raise
        return user.id


def create_feedback(db: Session, feedback: Union[FeedbackCreate, dict]):
    if isinstance(feedback, dict):
        feedback = FeedbackCreate(**feedback)

    enriched = enrich_feedback_data(feedback.text)
    feedback.sentiment = enriched["sentiment"]
    feedback.sentiment_score = enriched["sentiment_score"]
    feedback.topics = enriched["topics"]

    user_id = get_or_create_user_id(
        db,
        email=feedback.email,
        mobile=feedback.mobile,
        name=feedback.name,
        company_id=feedback.company_id,
    )

    payload = feedback.model_dump()
    payload["email"] = _normalize_email(feedback.email)
    payload["mobile"] = _normalize_mobile(feedback.mobile)
    db_feedback = Feedback(**payload, user_id=user_id)
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

        user_id = get_or_create_user_id(
            db,
            email=feedback.email,
            mobile=feedback.mobile,
            name=feedback.name,
            company_id=feedback.company_id,
        )
        payload = feedback.model_dump()
        payload["email"] = _normalize_email(feedback.email)
        payload["mobile"] = _normalize_mobile(feedback.mobile)
        db_feedbacks.append(Feedback(**payload, user_id=user_id))
    db.add_all(db_feedbacks)
    db.commit()
    for fb in db_feedbacks:
        db.refresh(fb)
    return db_feedbacks

