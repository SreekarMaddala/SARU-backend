from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.app.modules.users.model import User
from backend.app.modules.users.schema import UserCreate


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


def get_user_by_email_or_mobile(db: Session, email_or_mobile: str):
    normalized_email = _normalize_email(email_or_mobile)
    normalized_mobile = _normalize_mobile(email_or_mobile)
    return db.query(User).filter(
        or_(User.email == normalized_email, User.mobile == normalized_mobile)
    ).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate):
    payload = user.model_dump()
    payload["email"] = _normalize_email(payload.get("email"))
    payload["mobile"] = _normalize_mobile(payload.get("mobile"))
    db_user = User(**payload)
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception:
        db.rollback()
        existing = None
        if payload.get("email"):
            existing = db.query(User).filter(User.email == payload["email"]).first()
        if existing is None and payload.get("mobile"):
            existing = db.query(User).filter(User.mobile == payload["mobile"]).first()
        if existing is not None:
            return existing
        raise

