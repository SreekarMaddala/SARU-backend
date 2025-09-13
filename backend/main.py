from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db
from models import Feedback
from schemas import FeedbackCreate, Feedback
from crud import get_feedbacks, create_feedback, create_feedbacks_bulk
import pandas as pd
import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import imaplib
import email
import tweepy

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"msg": "Hello MVP 🚀"}

@app.get("/feedback", response_model=list[Feedback])
def read_feedbacks(db: Session = Depends(get_db)):
    feedbacks = get_feedbacks(db)
    return feedbacks

@app.post("/feedback", response_model=Feedback)
def create_new_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    return create_feedback(db, feedback)

@app.post("/feedback/upload_csv")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    df = pd.read_csv(file.file)
    feedbacks = []
    for _, row in df.iterrows():
        feedback = FeedbackCreate(company_id=str(row['company_id']), channel=str(row['channel']), text=str(row['text']))
        feedbacks.append(feedback)
    inserted = create_feedbacks_bulk(db, feedbacks)
    return {"inserted": inserted}

@app.post("/feedback/import_google_forms")
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

@app.post("/feedback/import_emails")
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

@app.post("/feedback/import_twitter")
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
