from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.app.db.session import get_db
from backend.app.modules.auth.service import get_current_admin, ADMIN_EMAIL, ADMIN_PASSWORD
from backend.app.modules.auth.utils import create_access_token
from backend.app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/admin", tags=["admin"])


class AdminLogin(BaseModel):
    email: str
    password: str


@router.post("/login")
def admin_login(admin_credentials: AdminLogin, db: Session = Depends(get_db)):
    if admin_credentials.email != ADMIN_EMAIL or admin_credentials.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin_credentials.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "message": "Admin login successful"}


@router.get("/verify")
def verify_admin(current_admin: dict = Depends(get_current_admin)):
    return {"message": "Admin verified", "admin": current_admin}

