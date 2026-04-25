from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from backend.app.core.config import SECRET_KEY, ALGORITHM
from backend.app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="company/login")

ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "sreekar"


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

