from collections import Counter
from datetime import datetime, timedelta
from textblob import TextBlob
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from backend.app.modules.analytics.queries import get_feedback_df
from backend.app.modules.feedback.model import Feedback
from backend.app.modules.users.model import User
from backend.app.modules.products.model import Product


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
    df["user_key"] = df["email"].fillna(df["mobile"]).fillna("unknown")
    user_freq = df["user_key"].value_counts().to_dict()
    user_sentiment = df.groupby("user_key")["sentiment_score"].mean().to_dict()
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
    unique_users = df["user_id"].nunique() if "user_id" in df.columns else 0
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


def customer_retention_service(db: Session, company_id: int):
    feedback_rows = (
        db.query(Feedback.user_id, Feedback.created_at)
        .filter(Feedback.company_id == company_id, Feedback.user_id.isnot(None))
        .all()
    )
    if not feedback_rows:
        return {
            "summary": {"retained_customers": 0, "churned_customers": 0},
            "retention_over_time": [],
        }

    # Deterministic monthly retention:
    # retained = users active in both previous and current month
    # churned = users active in previous month but not current month
    # new = users active in current month but not previous month
    month_users: dict[str, set[int]] = {}
    for user_id, created_at in feedback_rows:
        period = created_at.strftime("%Y-%m")
        month_users.setdefault(period, set()).add(user_id)

    periods = sorted(month_users.keys())
    retention_over_time = []
    prev_users: set[int] = set()
    latest_churned = 0
    for period in periods:
        current_users = month_users[period]
        retained = len(current_users.intersection(prev_users))
        churned = len(prev_users.difference(current_users))
        new_customers = len(current_users.difference(prev_users))
        baseline = len(prev_users)
        retention_rate = round((retained / baseline) * 100, 2) if baseline else 0.0
        churn_rate = round((churned / baseline) * 100, 2) if baseline else 0.0
        retention_over_time.append(
            {
                "period": period,
                "retention_rate": retention_rate,
                "churn_rate": churn_rate,
                "retained_customers": retained,
                "new_customers": new_customers,
            }
        )
        latest_churned = churned
        prev_users = current_users

    latest = retention_over_time[-1]
    return {
        "summary": {
            "retained_customers": latest["retained_customers"],
            "churned_customers": latest_churned,
        },
        "retention_over_time": retention_over_time,
    }


def customer_profile_service(db: Session, company_id: int, customer_id: int):
    user = (
        db.query(User)
        .filter(User.company_id == company_id, User.id == customer_id)
        .first()
    )
    if not user:
        return None

    feedback_q = db.query(Feedback).filter(
        Feedback.company_id == company_id, Feedback.user_id == customer_id
    )
    feedback_rows = feedback_q.all()
    feedback_count = len(feedback_rows)
    avg_sentiment = (
        float(np.mean([f.sentiment_score for f in feedback_rows if f.sentiment_score is not None]))
        if feedback_rows
        else None
    )
    last_feedback_at = (
        max((f.created_at for f in feedback_rows), default=None)
        if feedback_rows
        else None
    )

    product_counts: dict[str, int] = {}
    for row in feedback_rows:
        if row.product_model_number:
            product_counts[row.product_model_number] = product_counts.get(
                row.product_model_number, 0
            ) + 1

    top_products = []
    if product_counts:
        models = list(product_counts.keys())
        products = (
            db.query(Product)
            .filter(Product.company_id == company_id, Product.model_number.in_(models))
            .all()
        )
        name_by_model = {p.model_number: p.name for p in products}
        for model, count in sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            top_products.append(
                {
                    "model_number": model,
                    "name": name_by_model.get(model),
                    "feedback_count": count,
                }
            )

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "mobile": user.mobile,
        "created_at": user.created_at,
        "total_feedback_count": feedback_count,
        "average_sentiment": avg_sentiment,
        "last_feedback_at": last_feedback_at,
        "top_products": top_products,
    }

