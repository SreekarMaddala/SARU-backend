from sqlalchemy.orm import Session
from backend.models.company import Company
from backend.schemas.company_schema import CompanyCreate

def get_company_by_email(db: Session, email: str):
    return db.query(Company).filter(Company.email == email).first()

def create_company(db: Session, company: CompanyCreate):
    # Store plain password as requested; do NOT use in production
    db_company = Company(
        name=company.name,
        email=company.email,
        password=company.password,
        password_hash=None,
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def authenticate_company(db: Session, email: str, password: str):
    company = get_company_by_email(db, email)
    if not company:
        return False
    # Plain password only (no bcrypt)
    if company.password is None:
        return False
    if password != company.password:
        return False
    return company
