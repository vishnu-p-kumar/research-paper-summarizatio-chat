# AI Research Paper Summarizer + Chat

Full-stack app for uploading research papers, generating structured summaries, and chatting with papers through retrieval-augmented generation.

## Stack

- Frontend: React + Vite + Tailwind CSS
- Backend: FastAPI
- Database: PostgreSQL
- Auth: JWT in HttpOnly cookies
- AI provider: Google Gemini API
- Deployment target: Vercel

## Free-Tier Friendly Services

- Vercel Hobby can host the frontend and serverless API.
- Neon Postgres has a free tier suitable for testing and small projects.
- RAG embeddings use deterministic hashing in code, so no paid embedding API is required.
- Web fallback uses DuckDuckGo HTML scraping, so no paid search API key is required.
- Gemini API may provide free quota with rate limits through Google AI Studio. Check your account quota before public use.

## Vercel Environment Variables

Add these in Vercel Project Settings -> Environment Variables:

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

Do not set `VITE_API_BASE_URL` on Vercel when frontend and backend are deployed in the same Vercel project. The frontend uses same-origin `/api/*` routes in production.

## Local Environment Files

Use these templates:

- `.env.example`: backend env variables with comments
- `.env.vercel.example`: Vercel env variables
- `backend/.env.example`: local backend env template
- `frontend/.env.example`: local frontend env template

Real secrets should go only in:

- `backend/.env`
- `frontend/.env.local`
- Vercel Environment Variables

## API Endpoints

- `POST /register`
- `POST /login`
- `POST /logout`
- `POST /forgot-password`
- `POST /reset-password`
- `GET /me`
- `POST /upload/pdf`
- `POST /upload/url`
- `POST /summarize`
- `POST /chat`
- `GET /models`
- `GET /health`

## Copy-Paste Local Run Commands

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

Then open:

```text
http://localhost:5173
```
