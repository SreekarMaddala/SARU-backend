# TODO: Add Products Feature

## Steps to Complete

- [ ] Create Product SQLAlchemy model in backend/models/product.py
- [ ] Update backend/models/__init__.py to import Product
- [ ] Create Alembic migration for products table
- [ ] Create Pydantic schemas in backend/schemas/product_schema.py
- [ ] Create CRUD operations in backend/crud/product_crud.py
- [ ] Create routes in backend/routes/product_routes.py (protected with company auth)
- [ ] Update backend/main.py to include the product router
- [ ] Check and update auth.py if needed for company dependency
- [ ] Test the implementation
