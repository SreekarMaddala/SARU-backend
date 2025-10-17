from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.company import Company
from backend.schemas.company_schema import CompanyCreate, Company, Token, CompanyLogin
from backend.crud.company_crud import create_company, authenticate_company, get_company_by_email
from backend.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

# Removed legacy admin bypass for company login

router = APIRouter(prefix="/company", tags=["company"])

@router.post("/register", response_model=Company)
def register_company(company: CompanyCreate, db: Session = Depends(get_db)):
    db_company = get_company_by_email(db, email=company.email)
    if db_company:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_company(db, company)

@router.post("/login", response_model=Token)
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

# Single JSON-based login endpoint only
