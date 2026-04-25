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
# import snscrape.modules.twitter as sntwitter  # <- replaced Tweepy - DISABLED (Python 3.13 incompatible)

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
    required_cols = ['channel', 'text', 'name', 'email_or_mobile']
    if not set(required_cols).issubset(df.columns):
        raise HTTPException(status_code=400, detail=f"CSV must contain columns: {', '.join(required_cols)}")
    if df.empty:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    feedbacks = []
    for _, row in df.iterrows():
        feedback = FeedbackCreate(
            company_id=current_company.id,
            channel=str(row['channel']),
            text=str(row['text']),
            name=str(row['name']),
            email_or_mobile=str(row['email_or_mobile']),
            product_id=int(row['product_id']) if 'product_id' in df.columns and pd.notna(row['product_id']) else None,
        )
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
        # Assume row[0] is name, row[1] is text, row[2] is email_or_mobile, etc.
        name = row[0] if len(row) > 0 else "Anonymous"
        text = row[1] if len(row) > 1 else ""
        email_or_mobile = row[2] if len(row) > 2 else "unknown@google.com"
        feedback = FeedbackCreate(
            company_id=current_company.id,
            channel='google_forms',
            text=text,
            name=name,
            email_or_mobile=email_or_mobile,
            product_id=None,
        )
        feedbacks.append(feedback)
    inserted = create_feedbacks_bulk(db, feedbacks)
    return {"inserted": len(inserted)}

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
        # Extract sender email as email_or_mobile, use subject as name or default
        sender = msg['from']
        name = subject if subject else "Email User"
        email_or_mobile = sender if sender else "unknown@email.com"
        feedback = FeedbackCreate(
            company_id=current_company.id,
            channel='email',
            text=f"{subject}: {body}",
            name=name,
            email_or_mobile=email_or_mobile,
            product_id=None,
        )
        feedbacks.append(feedback)
    inserted = create_feedbacks_bulk(db, feedbacks)
    return {"inserted": len(inserted)}

@router.post("/feedback/import_twitter")\ndef import_twitter(\n    handle: str,\n    db: Session = Depends(get_db),\n    current_company=Depends(get_current_company)\n):\n    return {"error": "Twitter import disabled (snscrape incompatible with Python 3.13)"}\n\n# DISABLED: snscrape Twitter scraper (Python 3.13 incompatible)\n# Original code commented out for reference:
