from ..database import get_db
from ..crud.feedback_crud import create_feedback, get_feedbacks
from ..schemas.feedback_schema import FeedbackCreate
from sqlalchemy.orm import Session

def test_db_connection():
    db = next(get_db())
    test_feedback = FeedbackCreate(company_id="test_company", channel="test_channel", text="Test feedback")
    created_feedback = create_feedback(db, test_feedback)
    print("Created feedback:", created_feedback)
    feedbacks = get_feedbacks(db)
    found = any(f.id == created_feedback.id for f in feedbacks)
    print("Test feedback found in DB:", found)
    return found

if __name__ == "__main__":
    success = test_db_connection()
    if success:
        print("Database connection and data input test succeeded.")
    else:
        print("Database connection and data input test failed.")
