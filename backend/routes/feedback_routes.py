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
import tweepy

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
    feedbacks = []
    for _, row in df.iterrows():
        feedback = FeedbackCreate(company_id=str(row['company_id']), channel=str(row['channel']), text=str(row['text']))
        feedbacks.append(feedback)
    inserted = create_feedbacks_bulk(db, feedbacks)
    return {"inserted": inserted}

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

@router.post("/feedback/import_twitter")
def import_twitter(handle: str, db: Session = Depends(get_db)):
    client = tweepy.Client(bearer_token=os.getenv('TWITTER_BEARER_TOKEN'))
    user = client.get_user(username=handle)
    tweets = client.get_users_mentions(id=user.data.id, max_results=10)
    feedbacks = []
    for tweet in tweets.data:
        feedback = FeedbackCreate(company_id='default', channel='twitter', text=tweet.text)
        feedbacks.append(feedback)
    inserted = create_feedbacks_bulk(db, feedbacks)
    return {"inserted": inserted}
