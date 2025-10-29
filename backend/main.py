# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routes.feedback_routes import router as feedback_router
from .routes.company_routes import router as company_router
from .routes.product_routes import router as product_router
from .routes.user_routes import router as user_router
from .routes.admin_routes import router as admin_router
from .routes.analytics_routes import router as analytics_router
from .routes.sentiment_routes import router as sentiment_router
from .routes.topic_routes import router as topic_router
from .routes.channel_routes import router as channel_router
from .models.company import Company  # import your models

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
app.include_router(user_router)
app.include_router(analytics_router)
app.include_router(sentiment_router)
app.include_router(topic_router)
app.include_router(channel_router)

@app.get("/")
def read_root():
    return {"msg": "Hello MVP 🚀"}
