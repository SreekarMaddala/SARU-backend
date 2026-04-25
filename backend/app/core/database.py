from sqlalchemy import create_engine
from backend.app.core.config import DATABASE_URL
from backend.app.db.base import Base

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

