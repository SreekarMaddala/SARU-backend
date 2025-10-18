# TODO: Add Company Authentication & Protected Feedback API

## Steps to Complete

- [x] Update requirements.txt: Add python-jose[cryptography], passlib[bcrypt]
- [x] Create Company model: backend/models/company.py with id, name, email, password_hash, created_at
- [x] Update Feedback model: Change company_id to Integer ForeignKey to Company.id
- [x] Create Company schemas: backend/schemas/company_schema.py (CompanyBase, CompanyCreate, Company, CompanyLogin)
- [x] Create Company CRUD: backend/crud/company_crud.py (create_company, authenticate_company, get_company_by_email)
- [x] Create Company routes: backend/routes/company_routes.py (register, login)
- [x] Create auth dependencies: backend/auth.py (get_current_company, create_access_token)
- [x] Update feedback routes: Add Depends(get_current_company) to all routes, update to use company.id
- [x] Update feedback CRUD: Filter feedbacks by company_id
- [x] Update feedback schemas: Remove company_id from input schemas (injected from token)
- [x] Run alembic migration: alembic revision --autogenerate -m "Add Company model and update Feedback"
- [x] Update main.py: Include company_router
- [x] Test: Register company, login, access protected routes

# TODO: Implement Feedback Enrichment

## Steps to Complete

- [x] Update requirements.txt: Add textblob for sentiment analysis
- [x] Create User model: backend/models/user.py with id, email_or_mobile, name, created_at
- [x] Update Feedback model: Change user_id to ForeignKey to User.id
- [x] Update feedback schemas: Add name to FeedbackCreate input
- [x] Modify feedback_crud.py: Add enrichment function to analyze text, extract topics, handle user lookup/create
- [x] Update backend/models/__init__.py: Import new User model
- [ ] Run alembic migration: alembic revision --autogenerate -m "Add User model and update Feedback for enrichment"
- [ ] Update routes if needed to pass name in input
- [x] Install new dependencies
- [x] Test enrichment with sample data
