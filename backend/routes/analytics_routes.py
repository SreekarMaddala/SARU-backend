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



# 4. User Behavior Analysis
@router.get("/users")
def user_behavior_analysis(db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    df = get_feedback_df(db, current_company.id)
    if df.empty:
        return []
    user_freq = df['email_or_mobile'].value_counts().to_dict()
    user_sentiment = df.groupby('email_or_mobile')['sentiment_score'].mean().to_dict()
    data = []
    for user in user_freq:
        data.append({
            'user_id': user,
            'feedback_count': user_freq[user],
            'avg_sentiment': user_sentiment.get(user, 0)
        })
    return data

# 5. Company Performance Analysis (assuming multiple companies, but per company)
@router.get("/company-performance")
def company_performance_analysis(db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    df = get_feedback_df(db, current_company.id)
    if df.empty:
        return {"total_feedback": 0, "avg_sentiment": 0, "total_topics": 0, "unique_users": 0, "topic_counts": {}}
    total_feedback = len(df)
    avg_sentiment = df['sentiment_score'].mean()
    topic_counts = Counter([t for topics in df['topics'].dropna() for t in topics.split(',')])
    total_topics = len(topic_counts)
    unique_users = df['email_or_mobile'].nunique()
    return {"total_feedback": total_feedback, "avg_sentiment": avg_sentiment, "total_topics": total_topics, "unique_users": unique_users, "topic_counts": dict(topic_counts)}

# 6. Product Feedback Analysis
@router.get("/products")
def product_feedback_analysis(db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    df = get_feedback_df(db, current_company.id)
    if df.empty:
        return {"message": "No feedback data available"}
    product_df = df.dropna(subset=['product_id'])
    if product_df.empty:
        return {"message": "No product-specific feedback"}
    product_sentiment = product_df.groupby('product_id')['sentiment_score'].mean().to_dict()
    product_counts = product_df['product_id'].value_counts().to_dict()
    return {"product_avg_sentiment": product_sentiment, "product_feedback_counts": product_counts}

# 7. Temporal Analysis
@router.get("/temporal")
def temporal_analysis(db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    df = get_feedback_df(db, current_company.id)
    if df.empty:
        return []
    df['date'] = pd.to_datetime(df['created_at']).dt.date
    daily_counts = df.groupby('date').size().to_dict()
    daily_sentiment = df.groupby('date')['sentiment_score'].mean().to_dict()
    data = []
    for date in daily_counts:
        data.append({
            'date': str(date),
            'feedback_count': daily_counts[date],
            'avg_sentiment': daily_sentiment.get(date, 0)
        })
    return data
