# TODO: Update User Primary Key to email_or_mobile and Link Feedback Directly

## Steps to Complete

- [x] Update backend/models/user.py: Remove 'id' column, make 'email_or_mobile' the primary key.
- [ ] Update backend/models/feedback.py: Change 'user_id' to 'user_email_or_mobile' (ForeignKey to users.email_or_mobile), remove 'email_or_mobile' and 'user_ref' columns.
- [ ] Update backend/schemas/feedback_schema.py: Change 'user_id' to 'user_email_or_mobile' as str (required), remove 'email_or_mobile' and 'user_ref'.
- [ ] Update backend/crud/feedback_crud.py: Simplify get_or_create_user to just check existence, update create_feedback and create_feedbacks_bulk to set 'user_email_or_mobile' instead of 'user_id'.
- [ ] Generate new Alembic migration for schema changes (drop id, make email_or_mobile PK, update feedback FK, drop email_or_mobile and user_ref).
- [ ] Run the Alembic migration to apply changes to the database.
- [ ] Test the changes (e.g., create feedback, verify user linking).
