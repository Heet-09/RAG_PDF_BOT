# backend/main.py
from fastapi import FastAPI, UploadFile, File, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, FileResponse
from fastapi import HTTPException
from models import User
from middleware.rate_limit import RateLimitMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from fastapi import Header
import json
import shutil
import os


from models import UserPDF,Conversation, Message
from db import SessionLocal
from chat_history import (
    get_or_create_conversation,
    save_message,
    get_langchain_messages,
    maybe_update_summary,
)

from rag import (
    build_collection,
    collection_name_from_filename,
    load_mapping,
    save_mapping,
    # ask_question,
    UPLOAD_DIR,
    ask_question_stream
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limit middleware
app.add_middleware(RateLimitMiddleware)


@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    x_user_id: int = Header(...)
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    collection = collection_name_from_filename(
        f"{x_user_id}_{file.filename}"
    )

    build_collection(file_path, collection)

    db = SessionLocal()
    pdf = UserPDF(
        user_id=x_user_id,
        collection_name=collection,
        filename=file.filename
    )
    db.add(pdf)
    db.commit()
    db.close()

    return {
        "message": "PDF indexed",
        "collection": collection
    }


@app.get("/collections")
def get_collections(x_user_id: int = Header(...)):
    db = SessionLocal()

    pdfs = (
        db.query(UserPDF)
        .filter(UserPDF.user_id == x_user_id)
        .all()
    )

    result = {
        pdf.collection_name: pdf.filename
        for pdf in pdfs
    }

    db.close()
    return result

@app.post("/ask")
def ask(data: dict, x_user_id: int = Header(...)):
    
    print("\n🟢 [ASK] Incoming /ask request")
    print(f"📦 [ASK] Raw payload: {data}")

    collections = data.get("collections")
    question = data.get("question")

    if not isinstance(collections, list) or len(collections) > 3:
        return {"error": "Select up to 3 PDFs only"}

    # Conversation
    conversation_id = data.get("conversation_id")

    if conversation_id:
        conversation_id = int(conversation_id)
    else:
        conversation_id = get_or_create_conversation(
            user_id=x_user_id,
            collections=collections
        )

    # Save user message
    save_message(conversation_id, "user", question)

    def stream():
        full_answer = ""

        history = get_langchain_messages(conversation_id)

        try:
            for chunk in ask_question_stream(
                collections,
                question,
                history,
                conversation_id
            ):
                full_answer += chunk
                yield chunk

        except Exception as e:
            raise

        finally:
            if full_answer.strip():
                save_message(conversation_id, "assistant", full_answer)
                maybe_update_summary(conversation_id)

    return StreamingResponse(stream(), media_type="text/plain")

@app.get("/api/health")
def health(request: Request = None):
    print(f"[ENDPOINT] Full URL: {request.url}")
    return {"status": "ok"}

@app.post("/auth/signup")
def signup(username: str, password: str, request: Request = None):
    print(f"[ENDPOINT] Full URL: {request.url}")
    db = SessionLocal()
    try:
        user = User(username=username, password=password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"user_id": user.id, "username": user.username}

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username already exists")

    finally:
        db.close()


@app.post("/auth/login")
def login(username: str, password: str, request: Request = None):
    print(f"[ENDPOINT] Full URL: {request.url}")
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.password != password:
        raise HTTPException(status_code=401, detail="Invalid password")

    return {"user_id": user.id, "username": user.username}


@app.get("/conversations")
def list_conversations(x_user_id: int = Header(...), request: Request = None):
    print(f"[ENDPOINT] Full URL: {request.url}")
    db = SessionLocal()

    conversations = (
        db.query(Conversation)
        .filter(
            Conversation.user_id == x_user_id,
            Conversation.is_archived == False
        )
        .order_by(desc(Conversation.created_at))
        .all()
    )

    result = []
    for convo in conversations:
        pdfs = json.loads(convo.pdf_names)
        result.append({
            "id": convo.id,
            "pdf_names": pdfs,
            "created_at": convo.created_at.isoformat()
        })

    db.close()
    return result


@app.get("/conversations/{conversation_id}/messages")
def get_conversation_messages(
    conversation_id: int,
    x_user_id: int = Header(...),
    request: Request = None
):
    print(f"[ENDPOINT] Full URL: {request.url}")
    db = SessionLocal()

    convo = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == x_user_id
        )
        .first()
    )

    if not convo:
        db.close()
        return {"error": "Conversation not found"}

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .all()
    )

    db.close()

    return [
        {
            "role": m.role,
            "content": m.content
        }
        for m in messages
    ]



# Serve frontend static files
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")


