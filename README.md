# RAG PDF Chatbot (FastAPI + LangChain + Chroma)

A Retrieval-Augmented Generation (RAG) application where users can:

- Sign up and log in
- Upload PDF files
- Ask questions against one or more uploaded PDFs
- Receive streamed answers grounded in retrieved document chunks
- Keep per-user chat history and conversations

The backend is a FastAPI app and also serves the frontend static files from the `frontend/` folder.

## Project Structure

- `backend/`: API, RAG pipeline, DB models, conversation history
- `frontend/`: HTML/CSS/JS client pages
- `evaluation/`: offline evaluation scripts and datasets
- `render.yaml`: Render deployment config
- `Dockerfile`: container build for backend

## Key Features

- Hybrid retrieval: dense vectors (Chroma) + sparse BM25
- Reranking with cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`)
- Streaming answer generation (`/ask` endpoint)
- Multi-user isolation for uploaded PDFs
- Persistent chat/conversation storage in SQL database

## Tech Stack

- FastAPI, Uvicorn
- LangChain + LangChain Community
- ChromaDB
- HuggingFace embeddings (`all-MiniLM-L6-v2`)
- Groq LLM via `langchain-groq` (`openai/gpt-oss-120b`)
- SQLAlchemy + MySQL (default in current code)
- Vanilla HTML/CSS/JS frontend

## Prerequisites

- Python 3.11+
- pip
- A running MySQL-compatible database
- Groq API key

## Environment Variables

Create a `.env` file at the project root (`using_html/.env`).

Required values:

- `api_key`: your Groq API key
- `DATABASE_URL`: SQLAlchemy DB URL

Example:

```env
api_key=your_groq_api_key
DATABASE_URL=mysql+pymysql://username:password@127.0.0.1:3306/chatdb
```

Notes:

- The backend reads `.env` from project root in `backend/rag.py`.
- If `DATABASE_URL` is missing, code falls back to a hardcoded MySQL URL in `backend/db.py`.
- Do not commit real secrets.

## Local Setup (Windows PowerShell)

From workspace root 

1. Create and activate virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install backend dependencies

```powershell
pip install -r backend/requirements.txt
```

3. Initialize database tables

```powershell
cd backend
python init_db.py
cd ..
```

4. Start the API server

```powershell
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

5. Open app in browser

- `http://localhost:8000`

The frontend is served by FastAPI static mounting, so no separate frontend server is needed.

## First Run Flow

1. Open `http://localhost:8000/login.html`
2. Sign up (or log in)
3. Upload a PDF
4. Select up to 3 indexed PDFs
5. Ask questions and watch streamed responses

## API Endpoints (Main)

- `POST /auth/signup`
- `POST /auth/login`
- `POST /upload` (requires `X-User-Id` header)
- `GET /collections` (requires `X-User-Id` header)
- `POST /ask` (requires `X-User-Id` header, streaming response)
- `GET /conversations` (requires `X-User-Id` header)
- `GET /conversations/{conversation_id}/messages` (requires `X-User-Id` header)
- `GET /api/health`

## Evaluation

Evaluation scripts live in `evaluation/`.

Run from project root:

```powershell
python evaluation/run_rag_eval_runner.py
```

Before running, verify dataset and collection names inside:

- `evaluation/run_rag_eval_runner.py`
- `evaluation/golden_dataset_v1.json`

Outputs are written to `evaluation/eval_outputs/`.

## Deployment

- Render config: `render.yaml`
- Docker build: `Dockerfile`
- AWS build pipeline: `buildspec.yml`

Render start command currently uses:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

## Troubleshooting

- `ModuleNotFoundError` or import issues:
  - Run commands from the expected directory (`backend/` for local server commands).
- Database connection errors:
  - Recheck `DATABASE_URL` in `.env`.
  - Ensure MySQL host/user/password/database are valid and reachable.
- Upload works but answers fail:
  - Confirm `api_key` is set and valid.
  - Check backend logs for retrieval/LLM exceptions.
- Empty PDF list:
  - Ensure you are logged in and `X-User-Id` is being sent by frontend (stored in `localStorage`).

## Current Limitations

- Authentication currently stores plain passwords (not production-safe yet).
- Some schema pieces (for conversation summaries) may require additional migration SQL depending on DB state.
- `backend/requirements.txt` includes `pypdfcd`, which may not be needed; keep as-is unless you validate and clean dependencies.

## Suggested Next Improvements

1. Add password hashing (bcrypt/argon2) and JWT auth.
2. Add DB migrations (Alembic) including conversation summary tables.
3. Cache BM25 indexes per collection to reduce latency.
4. Add test coverage for auth, upload, and streaming ask endpoints.
