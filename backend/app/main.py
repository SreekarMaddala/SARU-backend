from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.database import engine
from backend.app.db.base import Base

# Import all models so Base.metadata includes them
from backend.app.modules.companies.model import Company
from backend.app.modules.users.model import User
from backend.app.modules.feedback.model import Feedback
from backend.app.modules.products.model import Product
from backend.app.modules.ai.model import AiInsight

from backend.app.modules.auth.routes import router as auth_router
from backend.app.modules.companies.routes import router as companies_router
from backend.app.modules.users.routes import router as users_router
from backend.app.modules.feedback.routes import router as feedback_router
from backend.app.modules.products.routes import router as products_router
from backend.app.modules.customers.routes import router as customers_router
from backend.app.modules.analytics.routes import router as analytics_router
from backend.app.modules.ai.routes import router as ai_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auto-create tables
Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(companies_router)
app.include_router(users_router)
app.include_router(feedback_router)
app.include_router(products_router)
app.include_router(customers_router)
app.include_router(analytics_router)
app.include_router(ai_router)


@app.get("/")
def read_root():
    return {"msg": "Hello MVP 🚀"}


@app.on_event("startup")
async def schedule_weekly_agentic_analysis():
    """Lightweight scheduler: runs weekly analysis for all companies."""
    import asyncio
    from sqlalchemy.orm import Session
    from backend.app.db.session import SessionLocal
    from backend.app.modules.companies.model import Company
    from backend.app.modules.ai.manager import AgenticAIManager

    async def worker():
        while True:
            db: Session = SessionLocal()
            try:
                companies = db.query(Company).all()
                for c in companies:
                    AgenticAIManager.analyze_and_store(db, c.id)
            finally:
                db.close()
            await asyncio.sleep(7 * 24 * 60 * 60)

    asyncio.create_task(worker())

