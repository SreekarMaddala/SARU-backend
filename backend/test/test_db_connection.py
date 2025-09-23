from backend.database import get_db
from backend.crud.feedback_crud import create_feedback, get_feedbacks
from backend.schemas.feedback_schema import FeedbackCreate
from sqlalchemy.orm import Session
from sqlalchemy import text


def test_db_connection():
    try:
        db: Session = next(get_db())

        # 1. Ensure a test company exists
        db.execute(
            text("""
            INSERT INTO companies (id, name)
            VALUES (:id, :name)
            ON CONFLICT (id) DO NOTHING
            """),
            {"id": 1, "name": "Test Company"}
        )
        db.commit()

        # 2. Create a test feedback entry
        test_feedback = FeedbackCreate(
            company_id=1,
            channel="app",
            text="This is a test feedback",
            sentiment="positive",
            topics="testing",
            likes=0,
            user_ref="tester"
        )
        created_feedback = create_feedback(db, test_feedback)

        print(
            f"✅ Created feedback -> "
            f"ID: {created_feedback.id}, "
            f"Company: {created_feedback.company_id}, "
            f"Channel: {created_feedback.channel}, "
            f"Text: {created_feedback.text}, "
            f"Likes: {created_feedback.likes}, "
            f"UserRef: {created_feedback.user_ref}"
        )

        # 3. Fetch feedbacks for company_id=1
        feedbacks = get_feedbacks(db, company_id=1)
        print("🔍 All feedback for company_id=1:")
        for f in feedbacks:
            print(
                f"- ID: {f.id}, Text: {f.text}, Likes: {f.likes}, UserRef: {f.user_ref}"
            )

        # 4. Confirm test feedback exists
        found = any(f.id == created_feedback.id for f in feedbacks)
        print("✅ Test feedback found in DB:", found)

        return found

    except Exception as e:
        print("❌ Error connecting to DB or inserting data:", e)
        return False


if __name__ == "__main__":
    success = test_db_connection()
    if success:
        print("🎉 Database connection and data input test succeeded.")
    else:
        print("⚠️ Database connection and data input test failed.")
