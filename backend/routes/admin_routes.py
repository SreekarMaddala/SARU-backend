from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from backend.database import get_db
from backend.models.company import Company
from backend.schemas.company_schema import CompanyCreate, Company
from backend.crud.company_crud import create_company, get_company_by_email
from backend.auth import create_access_token, oauth2_scheme
from passlib.context import CryptContext
from datetime import timedelta
from jose import JWTError, jwt

router = APIRouter(prefix="/admin", tags=["admin"])

# Admin credentials (hardcoded)
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "sreekar"

# JWT settings (from auth.py)
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Admin login schema
class AdminLogin(BaseModel):
    email: str
    password: str

# Dependency to check if user is admin
def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None or email != ADMIN_EMAIL:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return {"email": email}

# Admin login endpoint
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

# Get all companies (protected)
@router.get("/companies", response_model=List[Company])
def get_all_companies(current_admin: dict = Depends(get_current_admin), db: Session = Depends(get_db)):
    companies = db.query(Company).all()
    return companies

# Create a new company (protected)
@router.post("/companies", response_model=Company)
def create_new_company(company: CompanyCreate, current_admin: dict = Depends(get_current_admin), db: Session = Depends(get_db)):
    # Check if company with this email already exists
    db_company = get_company_by_email(db, email=company.email)
    if db_company:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return create_company(db=db, company=company)
