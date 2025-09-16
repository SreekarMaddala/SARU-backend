from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.feedback_routes import router as feedback_router
from .routes.company_routes import router as company_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(feedback_router)
app.include_router(company_router)

@app.get("/")
def read_root():
    return {"msg": "Hello MVP 🚀"}
