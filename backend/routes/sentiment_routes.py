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

# 1. Sentiment Analysis
@router.get("/analytics/sentiment")
def sentiment_analysis(db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    df = get_feedback_df(db, current_company.id)
    if df.empty:
        return {"message": "No feedback data available"}
    sentiments = []
    for text in df['text']:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        sentiment = 'positive' if polarity > 0 else 'negative' if polarity < 0 else 'neutral'
        sentiments.append({'text': text, 'sentiment': sentiment, 'score': polarity})
    return {"sentiments": sentiments}
