# TODO: Remove `id` from products, use composite PK (company_id, model_number)

## Plan

**Chosen option:** Remove `id` column and use a composite primary key `(company_id, model_number)` — `model_number` uniquely identifies a product within a company.

### Files to modify

| # | File | Change |
|---|---|---|
| 1 | `backend/app/modules/products/model.py` | Remove `id`, make PK = `UniqueConstraint("company_id", "model_number")` |
| 2 | `backend/app/modules/products/schema.py` | Remove `id` field, add `company_id` to base |
| 3 | `backend/app/modules/products/service.py` | Replace `get_product_by_id` with `get_product_by_company_and_model`, `get_products_by_company` filter non-null `model_number` |
| 4 | `backend/app/modules/products/routes.py` | Change path param from `product_id` to `model_number: str` |
| 5 | `backend/app/modules/feedback/model.py` | Change `product_id` FK to composite FK `(company_id, model_number)` |
| 6 | `backend/app/modules/feedback/routes.py` | Change CSV `product_id` -> `product_id` as string model_number; validate with company_id + model_number |
| 7 | `backend/app/modules/analytics/queries.py` | Remove `product_id` column, replace with `model_number` |
| 8 | `backend/app/modules/analytics/service.py` | Group by `model_number` instead of `product_id` |
| 9 | New file: `backend/app/migrations/versions/xxxx_remove_product_id_add_composite_pk.py` | Composite PK migration |

### Questions resolved

- `model_number` will be `nullable=False` because it's part of the PK.
- Existing rows without `model_number` will be rejected — requires backfill or cleanup before migrating.
- Feedback CSV upload will use `model_number` column instead of `product_id`.

## Progress

- [x] TODO file created
- [x] Step 1: Update `products/model.py`
- [x] Step 2: Update `products/schema.py`
- [x] Step 3: Update `products/service.py`
- [x] Step 4: Update `products/routes.py`
- [x] Step 5: Update `feedback/model.py`
- [x] Step 6: Update `feedback/routes.py`
- [x] Step 7: Update `analytics/queries.py`
- [x] Step 8: Update `analytics/service.py`
- [x] Step 9: Create Alembic migration
- [x] Step 10: Test import check (py_compile OK; full import blocked by missing psycopg2 in env, not code)

