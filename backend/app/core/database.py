from sqlalchemy import create_engine
from backend.app.core.config import DATABASE_URL
from backend.app.db.base import Base

engine = create_engine(DATABASE_URL)

