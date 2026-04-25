from collections import Counter
from datetime import datetime, timedelta
from textblob import TextBlob
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from backend.app.modules.analytics.queries import get_feedback_df


def sentiment_analysis_service(db: Session, company_id: int):
    df = get_feedback_df(db, company_id)
    if df.empty:
        return {"message": "No feedback data available"}
    sentiments = []
    for text in df['text']:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        sentiment = 'positive' if polarity > 0 else 'negative' if polarity < 0 else 'neutral'
        sentiments.append({'text': text, 'sentiment': sentiment, 'score': polarity})
    return {"sentiments": sentiments}


def topic_modeling_service(db: Session, company_id: int):
    df = get_feedback_df(db, company_id)
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


def channel_analysis_service(db: Session, company_id: int):
    df = get_feedback_df(db, company_id)
    if df.empty:
        return {"message": "No feedback data available"}
    channel_counts = df['channel'].value_counts().to_dict()
    avg_sentiment = df.groupby('channel')['sentiment_score'].mean().to_dict()
    return {"channel_counts": channel_counts, "avg_sentiment_per_channel": avg_sentiment}


def user_behavior_analysis_service(db: Session, company_id: int):
    df = get_feedback_df(db, company_id)
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


def company_performance_analysis_service(db: Session, company_id: int):
    df = get_feedback_df(db, company_id)
    if df.empty:
        return {"total_feedback": 0, "avg_sentiment": 0, "total_topics": 0, "unique_users": 0, "topic_counts": {}}
    total_feedback = len(df)
    avg_sentiment = df['sentiment_score'].mean()
    topic_counts = Counter([t for topics in df['topics'].dropna() for t in topics.split(',')])
    total_topics = len(topic_counts)
    unique_users = df['email_or_mobile'].nunique()
    return {"total_feedback": total_feedback, "avg_sentiment": avg_sentiment, "total_topics": total_topics, "unique_users": unique_users, "topic_counts": dict(topic_counts)}


def product_feedback_analysis_service(db: Session, company_id: int):
    df = get_feedback_df(db, company_id)
    if df.empty:
        return {"message": "No feedback data available"}
    product_df = df.dropna(subset=['product_model_number'])
    if product_df.empty:
        return {"message": "No product-specific feedback"}
    product_sentiment = product_df.groupby('product_model_number')['sentiment_score'].mean().to_dict()
    product_counts = product_df['product_model_number'].value_counts().to_dict()
    return {"product_avg_sentiment": product_sentiment, "product_feedback_counts": product_counts}


def temporal_analysis_service(db: Session, company_id: int):
    df = get_feedback_df(db, company_id)
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

