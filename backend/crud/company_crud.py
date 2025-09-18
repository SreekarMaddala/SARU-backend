from sqlalchemy.orm import Session
from backend.models.company import Company
from backend.schemas.company_schema import CompanyCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Default credentials for testing
DEFAULT_EMAIL = "eesha9999@gmail.com"
DEFAULT_PASSWORD = "sreekar"

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

def get_default_company(db: Session):
    # Check if default exists
    company = get_company_by_email(db, DEFAULT_EMAIL)
    if not company:
        hashed_password = pwd_context.hash(DEFAULT_PASSWORD)
        company = Company(
            name="Default Company",
            email=DEFAULT_EMAIL,
            password_hash=hashed_password
        )
        db.add(company)
        db.commit()
        db.refresh(company)
    return company

def authenticate_company(db: Session, email: str, password: str):
    # Return default company if credentials match
    if email == DEFAULT_EMAIL and password == DEFAULT_PASSWORD:
        return get_default_company(db)

    company = get_company_by_email(db, email)
    if not company:
        return False
    if not pwd_context.verify(password, company.password_hash):
        return False
    return company
