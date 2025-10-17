from sqlalchemy.orm import Session
from backend.models.company import Company
from backend.schemas.company_schema import CompanyCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_company_by_email(db: Session, email: str):
    return db.query(Company).filter(Company.email == email).first()

def create_company(db: Session, company: CompanyCreate):
    hashed_password = pwd_context.hash(company.password)
    db_company = Company(
        name=company.name,
        email=company.email,
        password_hash=hashed_password
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def authenticate_company(db: Session, email: str, password: str):
    company = get_company_by_email(db, email)
    if not company:
        return False
    # Support both hashed and legacy plain-text password
    if company.password_hash:
        if not pwd_context.verify(password, company.password_hash):
            return False
    elif company.password is not None:
        if password != company.password:
            return False
    else:
        return False
    return company
