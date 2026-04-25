from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.modules.users.model import User
from backend.app.core.security import get_current_company

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[dict])
def list_users(db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    users = db.query(User).filter(User.company_id == current_company.id).all()
    return [
        {
            "id": user.email_or_mobile,
            "name": user.name,
            "email": user.email_or_mobile,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        for user in users
    ]


@router.get("/test")
def test_users_endpoint():
    return {"message": "Users endpoint is working!"}


@router.get("/public", response_model=list[dict])
def list_users_public(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": user.email_or_mobile,
            "name": user.name,
            "email": user.email_or_mobile,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        for user in users
    ]

