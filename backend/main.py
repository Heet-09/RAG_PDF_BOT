from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, FileResponse
import shutil
import os

from chat_history import (
    get_or_create_conversation,
    save_message,
    get_langchain_messages
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

# Mount static files (frontend) at /static
app.mount("/static", StaticFiles(directory="../frontend"), name="frontend")

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    print("📥 [UPLOAD] Request received")
    print(f"📄 [UPLOAD] Filename: {file.filename}")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    print(f"📂 [UPLOAD] Saving file to: {file_path}")

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    print("✅ [UPLOAD] File saved successfully")

    collection = collection_name_from_filename(file.filename)
    print(f"🧠 [UPLOAD] Generated collection name: {collection}")

    build_collection(file_path, collection)
    print("📦 [UPLOAD] Chroma collection built")

    mapping = load_mapping()
    mapping[collection] = file.filename
    save_mapping(mapping)

    print("🗂️ [UPLOAD] collections.json updated")
    print("🎉 [UPLOAD] PDF indexing completed")

    return {"message": "PDF indexed", "collection": collection}


@app.get("/collections")
def get_collections():
    print("📚 [COLLECTIONS] Fetching all collections")
    mapping = load_mapping()
    print(f"📚 [COLLECTIONS] Found {len(mapping)} collections")
    return mapping


@app.post("/ask")
def ask(data: dict):
    collection = data["collection"]
    question = data["question"]

    conversation_id = get_or_create_conversation(collection)

    # Save user message
    save_message(conversation_id, "user", question)

    def stream():
        full_answer = ""

        history = get_langchain_messages(conversation_id)

        for chunk in ask_question_stream(
            collection,
            question,
            history
        ):
            full_answer += chunk
            yield chunk

        # Save assistant reply
        save_message(conversation_id, "assistant", full_answer)

    return StreamingResponse(stream(), media_type="text/plain")



@app.get("/api/health")
def health():
    return {"status": "ok"}


# Serve frontend static files
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
print(f"🌐 [INIT] Frontend directory: {FRONTEND_DIR}")
print(f"🌐 [INIT] Frontend exists: {os.path.exists(FRONTEND_DIR)}")
if os.path.exists(FRONTEND_DIR):
    print(f"🌐 [INIT] Mounting frontend static files")
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
else:
    print(f"❌ [INIT] Frontend directory not found!")
