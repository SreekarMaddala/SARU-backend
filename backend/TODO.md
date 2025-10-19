# TODO: Update User Primary Key to email_or_mobile and Link Feedback Directly

## Steps to Complete

- [x] Update backend/models/user.py: Remove 'id' column, make 'email_or_mobile' the primary key.
- [ ] Update backend/models/feedback.py: Change 'email_or_mobile' to 'user_email_or_mobile' (ForeignKey to users.email_or_mobile), remove 'user_ref' columns if any.
- [ ] Update backend/schemas/feedback_schema.py: Change 'email_or_mobile' to 'user_email_or_mobile' as str (required).
- [ ] Update backend/crud/feedback_crud.py: Update create_feedback and create_feedbacks_bulk to set 'user_email_or_mobile' instead of 'email_or_mobile'.
- [ ] Run the existing Alembic migration to apply changes to the database.
- [ ] Test the changes (e.g., create feedback, verify user linking).
