from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Feedback
from schemas import FeedbackCreate, Feedback
from crud import get_feedbacks, create_feedback

app = FastAPI()

@app.get("/")
def read_root():
    return {"msg": "Hello MVP 🚀"}

@app.get("/feedback", response_model=list[Feedback])
def read_feedbacks(db: Session = Depends(get_db)):
    feedbacks = get_feedbacks(db)
    return feedbacks

@app.post("/feedback", response_model=Feedback)
def create_new_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    return create_feedback(db, feedback)
