# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routes.feedback_routes import router as feedback_router
from .routes.company_routes import router as company_router
from .routes.product_routes import router as product_router
from .routes.agentic_routes import router as agentic_router
from .routes.user_routes import router as user_router
from .routes.admin_routes import router as admin_router
from .routes.analytics_routes import router as analytics_router
from .routes.sentiment_routes import router as sentiment_router
from .routes.topic_routes import router as topic_router
from .routes.channel_routes import router as channel_router
from .models.company import Company  # import your models
from .models.ai_insight import AiInsight  # ensure metadata includes ai_insights
from .models.product import Product  # ensure products present for FKs

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

# ✅ Auto-create tables
Base.metadata.create_all(bind=engine)

app.include_router(feedback_router)
app.include_router(company_router)
app.include_router(admin_router)
app.include_router(product_router)
app.include_router(agentic_router)
app.include_router(user_router)
app.include_router(analytics_router, prefix="/analytics")
app.include_router(sentiment_router)
app.include_router(topic_router)
app.include_router(channel_router)

@app.get("/")
def read_root():
    return {"msg": "Hello MVP 🚀"}


@app.on_event("startup")
async def schedule_weekly_agentic_analysis():
    """Lightweight scheduler: runs weekly analysis for all companies.

    For production, prefer a real scheduler (e.g., Celery beat or APScheduler).
    """
    import asyncio
    from sqlalchemy.orm import Session
    from .database import SessionLocal
    from .models.company import Company
    from .agentic_ai_manager import AgenticAIManager

    async def worker():
        while True:
            db: Session = SessionLocal()
            try:
                companies = db.query(Company).all()
                for c in companies:
                    AgenticAIManager.analyze_and_store(db, c.id)
            finally:
                db.close()
            # sleep 7 days
            await asyncio.sleep(7 * 24 * 60 * 60)

    asyncio.create_task(worker())
