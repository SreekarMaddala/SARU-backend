from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.feedback import Feedback
from backend.models.user import User
from backend.models.company import Company
from backend.models.product import Product
from backend.auth import get_current_company
from textblob import TextBlob
import pandas as pd
from collections import Counter
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.linear_model import LinearRegression
import numpy as np

router = APIRouter()

# Helper function to get feedback data as DataFrame
def get_feedback_df(db: Session, company_id: int):
    feedbacks = db.query(Feedback).filter(Feedback.company_id == company_id).all()
    data = [{
        'id': f.id,
        'company_id': f.company_id,
        'product_id': f.product_id,
        'channel': f.channel,
        'text': f.text,
        'sentiment': f.sentiment,
        'topics': f.topics,
        'email_or_mobile': f.email_or_mobile,
        'name': f.name,
        'sentiment_score': f.sentiment_score,
        'likes': f.likes,
        'created_at': f.created_at
    } for f in feedbacks]
    return pd.DataFrame(data)

# 3. Channel Analysis
@router.get("/analytics/channels")
def channel_analysis(db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    df = get_feedback_df(db, current_company.id)
    if df.empty:
        return {"message": "No feedback data available"}
    channel_counts = df['channel'].value_counts().to_dict()
    avg_sentiment = df.groupby('channel')['sentiment_score'].mean().to_dict()
    return {"channel_counts": channel_counts, "avg_sentiment_per_channel": avg_sentiment}
