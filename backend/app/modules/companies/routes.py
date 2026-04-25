from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.modules.companies.model import Company
from backend.app.modules.companies.schema import CompanyCreate, CompanyRead, CompanyLogin
from backend.app.modules.companies.service import create_company, authenticate_company, get_company_by_email
from backend.app.modules.auth.utils import create_access_token
from backend.app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/company", tags=["company"])


@router.post("/register", response_model=CompanyRead)
def register_company(company: CompanyCreate, db: Session = Depends(get_db)):
    db_company = get_company_by_email(db, email=company.email)
    if db_company:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_company(db, company)


@router.post("/login")
def login_company(credentials: CompanyLogin, db: Session = Depends(get_db)):
    company = authenticate_company(db, credentials.email, credentials.password)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": company.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

