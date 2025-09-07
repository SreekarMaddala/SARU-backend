# Feedback MVP

A full-stack feedback collection app with FastAPI backend and React frontend.

## Backend (FastAPI + PostgreSQL)

### Setup
1. Install dependencies: `pip install -r backend/requirements.txt`
2. Set up PostgreSQL database and update `backend/.env` with DATABASE_URL.
3. Run migrations: `cd backend && alembic upgrade head`
4. Start server: `uvicorn backend.main:app --reload`

### Endpoints
- GET `/`: Hello message
- GET `/feedback`: Get all feedback
- POST `/feedback`: Create new feedback

### Deployment
- Use Railway or Render for backend.
- Set DATABASE_URL in environment variables.
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Frontend (React + Tailwind)

### Setup
1. Install dependencies: `cd frontend && npm install`
2. Start dev server: `npm run dev`
3. Build: `npm run build`

### Deployment
- Use Vercel or Netlify.
- Build command: `npm run build`
- Publish directory: `dist`

## Database
- Use Neon or Supabase for PostgreSQL.
- Update DATABASE_URL in .env and deployment env vars.
