from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.feedback import Feedback
from ..schemas.feedback_schema import FeedbackCreate, Feedback, FeedbackBulkCreate
from ..crud.feedback_crud import get_feedbacks, create_feedback, create_feedbacks_bulk, create_feedbacks_bulk_chunked
import pandas as pd
import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import imaplib
import email
import tweepy

router = APIRouter()

# -----------------------------
# Get all feedbacks
# -----------------------------
@router.get("/feedback", response_model=list[Feedback])
def read_feedbacks(db: Session = Depends(get_db)):
    return get_feedbacks(db)


# -----------------------------
# Bulk insert (via API)
# -----------------------------
@router.post("/feedback/bulk")
def add_feedback_bulk(payload: FeedbackBulkCreate, db: Session = Depends(get_db)):
    created_feedbacks = create_feedbacks_bulk(db, payload)
    return {"inserted": len(created_feedbacks)}


# -----------------------------
# Upload CSV
# -----------------------------
@router.post("/feedback/upload_csv")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    df = pd.read_csv(file.file)
    feedbacks = [FeedbackCreate(
        company_id=str(row['company_id']),
        channel=str(row['channel']),
        text=str(row['text'])
    ) for _, row in df.iterrows()]

    payload = FeedbackBulkCreate(feedbacks=feedbacks)
    inserted = create_feedbacks_bulk(db, payload)
    return {"inserted": len(inserted)}


# -----------------------------
# Import Google Forms
# -----------------------------
@router.post("/feedback/import_google_forms")
def import_google_forms(sheet_id: str, db: Session = Depends(get_db)):
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/spreadsheets.readonly'])
    service = build('sheets', 'v4', credentials=creds)
    result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range='A1:D').execute()
    values = result.get('values', [])

    feedbacks = [
        FeedbackCreate(company_id=row[0], channel='google_forms', text=row[1])
        for row in values[1:]
    ]

    payload = FeedbackBulkCreate(feedbacks=feedbacks)
    inserted = create_feedbacks_bulk(db, payload)
    return {"inserted": len(inserted)}


# -----------------------------
# Import Emails
# -----------------------------
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

        feedbacks.append(FeedbackCreate(company_id='default', channel='email', text=f"{subject}: {body}"))

    payload = FeedbackBulkCreate(feedbacks=feedbacks)
    inserted = create_feedbacks_bulk(db, payload)
    return {"inserted": len(inserted)}


# -----------------------------
# Import Twitter
# -----------------------------
@router.post("/feedback/import_twitter")
def import_twitter(handle: str, db: Session = Depends(get_db)):
    client = tweepy.Client(bearer_token=os.getenv('TWITTER_BEARER_TOKEN'))
    user = client.get_user(username=handle)
    tweets = client.get_users_mentions(id=user.data.id, max_results=10)

    feedbacks = [FeedbackCreate(company_id='default', channel='twitter', text=tweet.text) for tweet in tweets.data]
    payload = FeedbackBulkCreate(feedbacks=feedbacks)
    inserted = create_feedbacks_bulk(db, payload)
    return {"inserted": len(inserted)}
