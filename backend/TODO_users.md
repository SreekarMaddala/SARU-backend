# TODO: Create /users/ Endpoint

- [x] Create backend/schemas/user_schema.py with UserBase, UserCreate, User schemas
- [x] Create backend/crud/user_crud.py with functions to get all users and get user by email
- [x] Create backend/routes/user_routes.py with GET /users endpoint, protected by admin auth
- [x] Update backend/schemas/__init__.py to import User schemas
- [x] Update backend/crud/__init__.py to import user_crud functions
- [x] Update backend/main.py to include the user_router
- [ ] Test the new endpoint using curl to ensure it returns user data without 404 and verify authentication
