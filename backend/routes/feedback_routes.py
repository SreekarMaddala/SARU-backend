from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.feedback import Feedback
from backend.schemas.feedback_schema import FeedbackCreate, Feedback, FeedbackBulkCreate
from backend.crud.feedback_crud import get_feedbacks, create_feedback, create_feedbacks_bulk
from backend.auth import get_current_company
import pandas as pd
import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import imaplib
import email
import snscrape.modules.twitter as sntwitter  # <- replaced Tweepy

router = APIRouter()

@router.get("/feedback", response_model=list[Feedback])
def read_feedbacks(db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    feedbacks = get_feedbacks(db, current_company.id)
    return feedbacks

@router.post("/feedback/bulk")
def add_feedback_bulk(feedbacks: list[FeedbackCreate], db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    # Inject company_id from token
    for fb in feedbacks:
        fb.company_id = current_company.id
    created_feedbacks = create_feedbacks_bulk(db, feedbacks)
    return {"inserted": len(created_feedbacks)}

@router.post("/feedback/upload_csv")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    df = pd.read_csv(file.file)
    required_cols = ['channel', 'text']
    if not set(required_cols).issubset(df.columns):
        raise HTTPException(status_code=400, detail=f"CSV must contain columns: {', '.join(required_cols)}")
    if df.empty:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    feedbacks = []
    for _, row in df.iterrows():
        feedback = FeedbackCreate(company_id=current_company.id, channel=str(row['channel']), text=str(row['text']))
        feedbacks.append(feedback)
    inserted = create_feedbacks_bulk(db, feedbacks)
    # Return count of inserted records
    return {"inserted": len(inserted)}

@router.post("/feedback/import_google_forms")
def import_google_forms(sheet_id: str, db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/spreadsheets.readonly'])
    service = build('sheets', 'v4', credentials=creds)
    result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range='A1:D').execute()
    values = result.get('values', [])
    feedbacks = []
    for row in values[1:]:
        feedback = FeedbackCreate(company_id=current_company.id, channel='google_forms', text=row[1])
        feedbacks.append(feedback)
    inserted = create_feedbacks_bulk(db, feedbacks)
    return {"inserted": inserted}

@router.post("/feedback/import_emails")
def import_emails(db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(os.getenv('GMAIL_USER'), os.getenv('GMAIL_PASS'))
    mail.select('inbox')
    status, messages = mail.search(None, 'UNSEEN')
    messages = messages[0].split()
    feedbacks = []
    for msg_id in messages:
        status, msg_data = mail.fetch(msg_id, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])
        subject = msg['subject']
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()
        feedback = FeedbackCreate(company_id=current_company.id, channel='email', text=f"{subject}: {body}")
        feedbacks.append(feedback)
    inserted = create_feedbacks_bulk(db, feedbacks)
    return {"inserted": inserted}

@router.post("/feedback/import_twitter")
def import_twitter(
    handle: str,
    db: Session = Depends(get_db),
    current_company=Depends(get_current_company)
):
    from datetime import datetime, timedelta
    from collections import defaultdict
    import snscrape.modules.twitter as sntwitter
    from backend.models.feedback import Feedback as FeedbackModel  # SQLAlchemy model

    feedbacks = []
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)

    # Inclusive "until" → add +1 day
    query = f"@{handle} since:{yesterday.date()} until:{(now + timedelta(days=1)).date()}"

    user_count = defaultdict(int)

    def is_recent_duplicate(text: str) -> bool:
        return db.query(FeedbackModel).filter(
            FeedbackModel.text == text,
            FeedbackModel.created_at >= yesterday
        ).first() is not None

    # Enforce 24h gap between fetches for this company
    latest_feedback = db.query(FeedbackModel).filter(
        FeedbackModel.channel == "twitter",
        FeedbackModel.company_id == current_company.id
    ).order_by(FeedbackModel.created_at.desc()).first()

    if latest_feedback:
        next_available_time = latest_feedback.created_at + timedelta(hours=24)
        if now < next_available_time:
            return {
                "inserted": 0,
                "message": f"You can fetch tweets again after {next_available_time.strftime('%Y-%m-%d %H:%M:%S')} UTC"
            }

    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
        username = tweet.user.username

        # Skip duplicates and limit per-user mentions
        if is_recent_duplicate(tweet.content):
            continue
        if user_count[username] >= 3:
            continue

        # ✅ Build SQLAlchemy Feedback model with all fields
        feedback = FeedbackModel(
            company_id=current_company.id,
            channel="twitter",
            text=tweet.content,
            user_ref=username,               # twitter handle
            likes=getattr(tweet, "likeCount", 0),  # safe fallback
            created_at=now
        )
        feedbacks.append(feedback)
        user_count[username] += 1

    if not feedbacks:
        return {
            "inserted": 0,
            "message": "No new tweets available after applying limits."
        }

    # ✅ Bulk insert raw Feedback models
    db.add_all(feedbacks)
    db.commit()

    return {"inserted": len(feedbacks)}
