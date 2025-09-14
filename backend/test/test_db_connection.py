from backend.database import get_db
from backend.crud.feedback_crud import create_feedback, get_feedbacks
from backend.schemas.feedback_schema import FeedbackCreate
from sqlalchemy.orm import Session
def test_db_connection():
    try:
        # Get a database session
        db = next(get_db())
        # Create a test feedback entry
        test_feedback = FeedbackCreate(company_id="boat", channel="app", text="i love you")
        created_feedback = create_feedback(db, test_feedback)
        print("Created feedback:", created_feedback)
        # Fetch all feedbacks and check if the created one exists
        feedbacks = get_feedbacks(db)
        found = any(f.id == created_feedback.id for f in feedbacks)
        print("Test feedback found in DB:", found)
        return found
    except Exception as e:
        print("Error connecting to DB or inserting data:", e)
        return False
if __name__ == "__main__":
    success = test_db_connection()
    if success:
        print("Database connection and data input test succeeded.")
    else:
        print("Database connection and data input test failed.")
