from sqlalchemy.orm import Session
from backend.app.modules.users.model import User
from backend.app.modules.users.schema import UserCreate


def get_user_by_email_or_mobile(db: Session, email_or_mobile: str):
    return db.query(User).filter(User.email_or_mobile == email_or_mobile).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

