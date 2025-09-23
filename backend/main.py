# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routes.feedback_routes import router as feedback_router
from .routes.company_routes import router as company_router
from .routes.admin_routes import router as admin_router
from .models.company import Company  # import your models

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Auto-create tables
Base.metadata.create_all(bind=engine)

app.include_router(feedback_router)
app.include_router(company_router)
app.include_router(admin_router)

@app.get("/")
def read_root():
    return {"msg": "Hello MVP 🚀"}
