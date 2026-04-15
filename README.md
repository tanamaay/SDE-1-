
# AI Media Q&A (Python + FastAPI + React)

Database: MySQL 8.4 via Docker Compose.

## Start Project (Backend + Frontend)

### Option 1: Docker (recommended)

1. Create `.env` from template.
   - Windows PowerShell:
     - `Copy-Item .env.example .env`
2. Open `.env` and set:
   - `OPENAI_API_KEY=your_key`
3. Start all services:
   - `docker compose up --build -d`
4. Open apps:
   - Frontend: [http://localhost:5173](http://localhost:5173)
   - Backend API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Health check: [http://localhost:8000/health](http://localhost:8000/health)
5. Stop services:
   - `docker compose down`

### Option 2: Run manually (without Docker)

Prerequisites:
- Python 3.11+
- Node.js 20+
- MySQL running locally on port `3306`

1. Start backend:
   - `cd backend`
   - `python -m venv .venv`
   - `.\.venv\Scripts\activate`
   - `pip install -r requirements.txt`
   - Set env variables in PowerShell:
     - `$env:OPENAI_API_KEY="your_key"`
     - `$env:DATABASE_URL="mysql+pymysql://mediaqa:mediaqa@localhost:3306/mediaqa"`
     - `$env:UPLOAD_DIR="./uploads"`
   - Run API:
     - `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

2. Start frontend in a new terminal:
   - `cd frontend`
   - `npm install`
   - `npm run dev -- --host 0.0.0.0 --port 5173`

3. Open:
   - Frontend: [http://localhost:5173](http://localhost:5173)
   - Backend docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Troubleshooting

- If CSS or UI updates are not visible, do a hard refresh: `Ctrl + F5`.
- If port `8000` is busy, stop conflicting container/process and restart.
- If Docker build fails with temporary SSL/network error, retry `docker compose up --build -d`.
- If OpenAI key is missing, app runs with fallback responses (not full AI output).

## Features

- Upload PDF/audio/video
- PDF text extraction via `pypdf`
- Audio/video transcription via Whisper API (`whisper-1`)
- Chat Q&A powered by OpenAI Chat Completions
- Semantic retrieval using FAISS vector search (OpenAI embeddings with fallback)
- Content summarization via OpenAI
- Topic timestamp extraction from transcript segments
- Backend media file endpoint and frontend "Play at timestamp" button
- CI pipeline with test coverage gate
# SDE-1-
