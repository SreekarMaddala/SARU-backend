from sqlalchemy.orm import Session
from backend.app.modules.companies.model import Company
from backend.app.modules.companies.schema import CompanyCreate


def get_company_by_email(db: Session, email: str):
    return db.query(Company).filter(Company.email == email).first()


def create_company(db: Session, company: CompanyCreate):
    db_company = Company(
        name=company.name,
        email=company.email,
        password=company.password,
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


def authenticate_company(db: Session, email: str, password: str):
    company = get_company_by_email(db, email)
    if not company:
        return False
    if company.password is None:
        return False
    if password != company.password:
        return False
    return company

