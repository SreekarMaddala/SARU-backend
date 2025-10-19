from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models.user import User
from backend.schemas.user_schema import User
from backend.routes.admin_routes import get_current_admin

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[User])
def get_all_users(current_admin: dict = Depends(get_current_admin), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
