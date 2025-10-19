# TODO: Ensure feedback insertion stores data in user table

## Steps to Complete

- [x] Run alembic upgrade to apply the user-related migration (87581d4ba42a)
- [x] Update Feedback model: Add user_ref (String, nullable) and likes (Integer, nullable) columns
- [x] Generate and run a new alembic migration for the added columns
- [x] Update feedback routes: Ensure FeedbackCreate includes name and email_or_mobile (make required or default to anonymous)
- [x] Modify feedback_crud.py: Handle missing user data by creating a default user if needed
- [ ] Test feedback insertion endpoints to verify user table storage (critical-path: bulk insert, csv upload, twitter import)
