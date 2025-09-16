from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.feedback import Feedback
from backend.schemas.feedback_schema import FeedbackCreate, Feedback, FeedbackBulkCreate
from backend.crud.feedback_crud import get_feedbacks, create_feedback, create_feedbacks_bulk
import pandas as pd
import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import imaplib
import email
import snscrape.modules.twitter as sntwitter  # <- replaced Tweepy

router = APIRouter()

@router.get("/feedback", response_model=list[Feedback])
def read_feedbacks(db: Session = Depends(get_db)):
    feedbacks = get_feedbacks(db)
    return feedbacks

@router.post("/feedback/bulk")
def add_feedback_bulk(feedbacks: list[FeedbackCreate], db: Session = Depends(get_db)):
    # Convert Pydantic objects to dicts
    feedback_dicts = [fb.dict() for fb in feedbacks]
    created_feedbacks = create_feedbacks_bulk(db, FeedbackBulkCreate(feedbacks=feedbacks))
    return {"inserted": len(created_feedbacks)}

@router.post("/feedback/upload_csv")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    df = pd.read_csv(file.file)
    required_cols = ['company_id', 'channel', 'text']
    if not set(required_cols).issubset(df.columns):
        raise HTTPException(status_code=400, detail=f"CSV must contain columns: {', '.join(required_cols)}")
    if df.empty:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    feedbacks = []
    for _, row in df.iterrows():
        feedback = FeedbackCreate(company_id=str(row['company_id']), channel=str(row['channel']), text=str(row['text']))
        feedbacks.append(feedback)
    inserted = create_feedbacks_bulk(db, feedbacks)
    # Return count of inserted records
    return {"inserted": len(inserted)}

@router.post("/feedback/import_google_forms")
def import_google_forms(sheet_id: str, db: Session = Depends(get_db)):
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/spreadsheets.readonly'])
    service = build('sheets', 'v4', credentials=creds)
    result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range='A1:D').execute()
    values = result.get('values', [])
    feedbacks = []
    for row in values[1:]:
        feedback = FeedbackCreate(company_id=row[0], channel='google_forms', text=row[1])
        feedbacks.append(feedback)
    inserted = create_feedbacks_bulk(db, feedbacks)
    return {"inserted": inserted}

@router.post("/feedback/import_emails")
def import_emails(db: Session = Depends(get_db)):
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
        feedback = FeedbackCreate(company_id='default', channel='email', text=f"{subject}: {body}")
        feedbacks.append(feedback)
    inserted = create_feedbacks_bulk(db, feedbacks)
    return {"inserted": inserted}

# ------------------- Updated Twitter Import with snscrape -------------------
@router.post("/feedback/import_twitter")
def import_twitter(handle: str, db: Session = Depends(get_db)):
    from datetime import datetime, timedelta
    from collections import defaultdict

    feedbacks = []
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)

    query = f"@{handle} since:{yesterday.date()} until:{now.date()}"

    # Track how many times each user has already been added
    user_count = defaultdict(int)

    # Function to check for duplicates in the last 24 hours
    def is_recent_duplicate(db: Session, text: str):
        existing = db.query(Feedback).filter(
            Feedback.text == text,
            Feedback.created_at >= yesterday
        ).first()
        return existing is not None

    # Check last fetch time for this handle to enforce 24-hour restriction
    latest_feedback = db.query(Feedback).filter(
        Feedback.channel == "twitter",
        Feedback.company_id == "default"
    ).order_by(Feedback.created_at.desc()).first()

    if latest_feedback:
        next_available_time = latest_feedback.created_at + timedelta(hours=24)
        if now < next_available_time:
            return {
                "inserted": 0,
                "message": f"You can fetch tweets again after {next_available_time.strftime('%Y-%m-%d %H:%M:%S')} UTC"
            }

    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
        username = tweet.user.username

        # Skip if tweet is duplicate
        if is_recent_duplicate(db, tweet.content):
            continue

        # Skip if user already has 3 mentions in last 24 hours
        if user_count[username] >= 3:
            continue

        feedback = FeedbackCreate(
            company_id="default",
            channel="twitter",
            text=tweet.content
        )
        feedbacks.append(feedback)

        # Increment user mention count
        user_count[username] += 1

        # Optional: limit total tweets per request
        # if i >= 1000:
        #     break

    inserted = create_feedbacks_bulk(db, feedbacks)

    # If no new tweets were inserted, return a message
    if not feedbacks:
        return {
            "inserted": 0,
            "message": "No new tweets available after applying 24-hour and per-user limits."
        }

    return {"inserted": len(inserted)}


