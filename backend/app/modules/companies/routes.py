from datetime import timedelta
from urllib.parse import parse_qs
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.modules.companies.schema import CompanyCreate, CompanyRead
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
async def login_company(
    request: Request,
    db: Session = Depends(get_db),
):
    payload_email = None
    payload_password = None

    content_type = (request.headers.get("content-type") or "").lower()
    if "application/json" in content_type:
        try:
            body = await request.json()
        except Exception:
            body = {}
        if isinstance(body, dict):
            payload_email = body.get("email") or body.get("username")
            payload_password = body.get("password")
    else:
        raw = (await request.body()).decode("utf-8")
        form = parse_qs(raw)
        payload_email = (form.get("email") or form.get("username") or [None])[0]
        payload_password = (form.get("password") or [None])[0]

    if not payload_email or not payload_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="email (or username) and password are required",
        )

    company = authenticate_company(db, payload_email, payload_password)
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

