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

# 2. Topic Modeling (using LDA on text)
@router.get("/analytics/topics")
def topic_modeling(db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    df = get_feedback_df(db, current_company.id)
    if df.empty:
        return {"message": "No feedback data available"}
    texts = df['text'].tolist()
    vectorizer = CountVectorizer(stop_words='english')
    X = vectorizer.fit_transform(texts)
    lda = LatentDirichletAllocation(n_components=5, random_state=42)
    lda.fit(X)
    topics = []
    for idx, topic in enumerate(lda.components_):
        top_words = [vectorizer.get_feature_names_out()[i] for i in topic.argsort()[-10:]]
        topics.append({"topic_id": idx, "top_words": top_words})
    return {"topics": topics}
