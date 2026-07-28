# AI Research Paper Summarizer + Chat

A full-stack research assistant for uploading papers, generating summaries, and asking paper-grounded questions through retrieval-augmented generation.

## Current Stack

- Frontend: React 18, Vite, Tailwind CSS
- Backend: FastAPI
- Auth: JWT access/refresh tokens in HttpOnly browser-session cookies
- Database: PostgreSQL
- ORM/migrations: SQLAlchemy ORM + Alembic
- RAG storage: PostgreSQL tables for documents, chunks, and JSONB embeddings
- Embeddings: deterministic hashing embedder in Python
- LLM provider: Google Gemini REST API
- Deployment: Vercel frontend + Vercel Python serverless FastAPI entrypoint

## Features

- Register, login, logout, forgot password, and reset password pages
- Protected dashboard and protected backend APIs
- PDF upload and URL ingestion
- Paper summary generation
- Paper-grounded chat with retrieved document chunks
- Session-only uploaded-paper state in the browser
- Uploaded paper information clears on page refresh or logout
- Summary and chat state remain while switching sections in the same page session
- Per-user document access checks
- PostgreSQL persistence for uploaded paper text/chunks

## Architecture

```text
Browser
  |
  | React + Vite frontend
  | - Auth pages
  | - Protected dashboard
  | - Upload / Summary / Chat UI
  | - Axios with credentials for HttpOnly cookies
  |
  v
Vercel routing
  |
  | Static frontend: frontend/dist
  | API rewrites: /api/*, /upload/*, /summarize, /chat, /models, /health
  |
  v
FastAPI serverless entrypoint
  api/index.py -> backend/app/main.py
  |
  | Routes
  | - auth.py
  | - upload.py
  | - summarize.py
  | - chat.py
  | - models.py
  |
  v
Services
  |
  | AuthService
  | - bcrypt password hashing
  | - JWT session cookies
  | - login rate limiting
  |
  | RagStore
  | - chunk text
  | - hash embeddings
  | - store documents/chunks in PostgreSQL
  | - retrieve top chunks by cosine similarity
  |
  | Summarizer + Gemini service
  | - chunk summaries
  | - final structured summary JSON
  | - equation explanations
  |
  v
External services
  |
  | PostgreSQL
  | Google Gemini API
  | DuckDuckGo HTML fallback, optional
```

## Important Project Files

```text
api/index.py
  Vercel Python entrypoint. Imports FastAPI app from backend/app/main.py.

vercel.json
  Vercel build and rewrite configuration.

backend/app/main.py
  FastAPI app factory, CORS, route registration, startup schema creation.

backend/app/config.py
  Environment variable configuration.

backend/app/routes/auth.py
  Register, login, logout, forgot password, reset password, and /me routes.

backend/app/routes/upload.py
  Protected PDF and URL upload routes.

backend/app/routes/summarize.py
  Protected summary route.

backend/app/routes/chat.py
  Protected RAG chat route.

backend/app/services/rag_pipeline.py
  PostgreSQL-backed document/chunk storage and retrieval.

backend/app/services/llama_service.py
  Compatibility wrapper around Google Gemini generateContent REST API.

backend/app/services/summarizer.py
  Paper chunk summarization, final summary JSON, equation detection/explanation.

backend/app/models/user.py
  SQLAlchemy user model.

backend/alembic/
  Alembic migration setup and users table migration.

frontend/src/App.jsx
  Route-aware app shell, auth redirects, protected dashboard shell.

frontend/src/AuthContext.jsx
  Frontend auth provider.

frontend/src/pages/AuthPages.jsx
  Login, register, forgot password, reset password pages.

frontend/src/pages/Dashboard.jsx
  Upload area, Summary/Chat section switching, in-memory document state.
```

## Data Flow

1. User logs in or registers.
2. Backend sets HttpOnly session cookies.
3. Frontend calls `/api/me` on load to restore the current session.
4. User uploads a PDF or URL.
5. Backend extracts text and stores:
   - `documents.doc_id`
   - `documents.user_id`
   - raw text
   - chunks
   - JSONB hash embeddings
6. Summary route loads the user-owned document text and calls Gemini.
7. Chat route retrieves top chunks for that user-owned document and calls Gemini with retrieved context.
8. Refreshing the browser page clears current uploaded-paper state in the frontend.
9. Logging out clears auth cookies and frontend uploaded-paper state.

## Database Tables

`users`

- `id`
- `full_name`
- `email`
- `password_hash`
- `created_at`
- `updated_at`

`documents`

- `doc_id`
- `user_id`
- `text`
- `created_at`

`document_chunks`

- `doc_id`
- `chunk_id`
- `content`
- `embedding`

The `users` table is managed by Alembic. The RAG tables are created automatically by the backend if missing.

## Environment Variables

Use the templates:

- `.env.example`
- `.env.vercel.example`
- `backend/.env.example`
- `frontend/.env.example`

Real secrets should go only in:

- `backend/.env`
- `frontend/.env.local`
- Vercel Environment Variables

Required backend/Vercel variables:

```env
DATABASE_URL=PASTE_YOUR_DATABASE_URL_HERE
JWT_SECRET_KEY=PASTE_A_LONG_RANDOM_JWT_SECRET_HERE
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=14
RESET_TOKEN_EXPIRE_MINUTES=30
COOKIE_SECURE=1
CORS_ORIGINS=https://your-app.vercel.app
GEMINI_API_KEY=PASTE_YOUR_GEMINI_API_KEY_HERE
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
MODEL_NAME=gemini-3.6-flash
GEMINI_FALLBACK_MODELS=gemini-flash-latest,gemini-3.5-flash,gemini-3.1-flash-lite
GEMINI_MAX_TOKENS=800
GEMINI_TEMPERATURE=0.2
ENABLE_WEB_FALLBACK=1
WEB_MAX_RESULTS=3
WEB_TIMEOUT_S=12
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_UPLOAD_MB=10
```

For local HTTP development:

```env
COOKIE_SECURE=0
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Frontend local variable:

```env
VITE_API_BASE_URL=http://localhost:8000
```

On Vercel, leave `VITE_API_BASE_URL` unset when frontend and backend are deployed together.

## Free-Tier Notes

- Vercel Hobby can host the app for personal projects.
- Neon Postgres has a free tier suitable for small projects.
- The hashing embedder requires no paid embedding API.
- DuckDuckGo fallback requires no paid API key, but it is best-effort.
- Gemini API may include free quota depending on your Google AI Studio account and region.

## API Endpoints

Auth:

- `POST /register`
- `POST /login`
- `POST /logout`
- `POST /forgot-password`
- `POST /reset-password`
- `GET /me`

Vercel-safe auth aliases used by the frontend:

- `POST /api/register`
- `POST /api/login`
- `POST /api/logout`
- `POST /api/forgot-password`
- `POST /api/reset-password`
- `GET /api/me`

Research APIs:

- `POST /upload/pdf`
- `POST /upload/url`
- `POST /summarize`
- `POST /chat`
- `GET /models`
- `GET /health`

Protected routes require the HttpOnly auth cookies.

## Local Development

Before running, replace:

- `PASTE_YOUR_DATABASE_URL_HERE`
- `PASTE_YOUR_GEMINI_API_KEY_HERE`
- `PASTE_A_LONG_RANDOM_JWT_SECRET_HERE`

Windows PowerShell:

```powershell
cd "C:\Users\vishnu\Desktop\AI Research Paper Summarizer + Chat"
Copy-Item ".env.example" "backend\.env" -Force
$envText = Get-Content "backend\.env"
$envText = $envText -replace '^DATABASE_URL=.*', 'DATABASE_URL=PASTE_YOUR_DATABASE_URL_HERE'
$envText = $envText -replace '^JWT_SECRET_KEY=.*', 'JWT_SECRET_KEY=PASTE_A_LONG_RANDOM_JWT_SECRET_HERE'
$envText = $envText -replace '^COOKIE_SECURE=.*', 'COOKIE_SECURE=0'
$envText = $envText -replace '^CORS_ORIGINS=.*', 'CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173'
$envText = $envText -replace '^GEMINI_API_KEY=.*', 'GEMINI_API_KEY=PASTE_YOUR_GEMINI_API_KEY_HERE'
$envText | Set-Content "backend\.env"
Copy-Item "frontend\.env.example" "frontend\.env.local" -Force
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
alembic -c ..\alembic.ini upgrade head
Start-Process powershell -ArgumentList '-NoExit','-Command','cd "C:\Users\vishnu\Desktop\AI Research Paper Summarizer + Chat\backend"; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000'
cd ..\frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## Verification Commands

Backend syntax check:

```powershell
python -m compileall api backend\app
```

Frontend production build:

```powershell
npm.cmd --prefix frontend run build
```

Root Vercel-style build:

```powershell
npm.cmd run build
```

## Deployment On Vercel

1. Push the repository to GitHub.
2. Import the repo into Vercel.
3. Add all required environment variables from `.env.vercel.example`.
4. Use the included `vercel.json`.
5. Deploy.

Expected Vercel settings:

- Build Command: `cd frontend && npm ci && npm run build`
- Output Directory: `frontend/dist`
- Python API entrypoint: `api/index.py`

## Operational Notes

- Browser refresh clears uploaded-paper state in the frontend.
- Logout clears auth cookies and uploaded-paper frontend state.
- Closing the tab/browser clears the frontend session marker, so reopening the app asks for login again.
- Switching between Summary and Chat keeps the current page state.
- Uploaded documents remain in PostgreSQL for backend retrieval while their `doc_id` is in memory.
- The reset password route currently logs a reset token server-side. For real production email delivery, connect an email provider such as Resend, SendGrid, or SES.
