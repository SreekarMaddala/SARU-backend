# Backend Restructure TODO

## Phase 1: Core Infrastructure
- [x] Create TODO.md
- [x] Create `backend/app/core/config.py`
- [x] Create `backend/app/core/security.py`
- [x] Create `backend/app/core/database.py`
- [x] Create `backend/app/db/base.py`
- [x] Create `backend/app/db/session.py`
- [x] Create `backend/app/utils/logger.py`
- [x] Create `backend/app/utils/helpers.py`

## Phase 2: Feature Modules
- [x] Create `backend/app/modules/auth/` (routes, schema, service, utils)
- [x] Create `backend/app/modules/companies/` (model, schema, service, routes)
- [x] Create `backend/app/modules/users/` (model, schema, service, routes)
- [x] Create `backend/app/modules/feedback/` (model, schema, service, routes)
- [x] Create `backend/app/modules/products/` (model, schema, service, routes)
- [x] Create `backend/app/modules/analytics/` (routes, service, queries, utils)
- [x] Create `backend/app/modules/ai/` (routes, service, manager, prompts)

## Phase 3: Entry Point & Migrations
- [x] Create `backend/app/main.py`
- [x] Move alembic to `backend/app/migrations/`
- [x] Update `alembic.ini`
- [x] Update `migrations/env.py`

## Phase 4: Cleanup
- [x] Delete old flat directories (`models/`, `routes/`, `schemas/`, `crud/`)
- [x] Delete old top-level files (`main.py`, `database.py`, `auth.py`, `agentic_ai_manager.py`, `check_columns.py`)
- [x] Remove duplicate `backend/alembic.ini`
- [x] Move `backend/test/` → `backend/tests/`

## Phase 5: Verification
- [x] Run import check (`python -c "from backend.app.main import app"`)

