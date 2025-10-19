from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.auth import get_current_company

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[dict])
def list_users(db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    users = db.query(User).all()
    return [
        {
            "id": user.email_or_mobile,  # Use email_or_mobile as ID since it's the primary key
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
    """Public endpoint for testing - no authentication required"""
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