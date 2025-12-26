import os
import json
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langchain_experimental.text_splitter import SemanticChunker

load_dotenv()

DB_PATH = "chroma_db"
UPLOAD_DIR = "uploads"
MAPPING_FILE = "collections.json"

os.makedirs(DB_PATH, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

print("🚀 [INIT] RAG system starting")
print(f"📂 [INIT] DB_PATH: {DB_PATH}")
print(f"📂 [INIT] UPLOAD_DIR: {UPLOAD_DIR}")

model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.7,
    max_retries=3,
)

print("🤖 [INIT] Groq LLM initialized")

def get_embeddings():
    print("🔢 [EMBEDDINGS] Loading HuggingFace embeddings")
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def load_mapping():
    if not os.path.exists(MAPPING_FILE):
        print("⚠️ [MAPPING] collections.json not found, returning empty mapping")
        return {}

    try:
        with open(MAPPING_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                print("⚠️ [MAPPING] collections.json is empty, returning empty mapping")
                return {}
            mapping = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"❌ [MAPPING] Invalid JSON in collections.json: {e}")
        print("⚠️ [MAPPING] Returning empty mapping")
        return {}

    print(f"🗂️ [MAPPING] Loaded {len(mapping)} collections")
    return mapping

def save_mapping(mapping):
    with open(MAPPING_FILE, "w") as f:
        json.dump(mapping, f, indent=2)

    print("💾 [MAPPING] collections.json saved")

def collection_name_from_filename(filename):
    name = os.path.splitext(filename)[0].replace(" ", "_").lower()
    print(f"🔤 [COLLECTION] Derived collection name: {name}")
    return name

def build_collection(file_path, collection_name):
    print(f"📦 [CHROMA] Building collection: {collection_name}")

    loader = PyPDFLoader(file_path)
    pages = loader.load()
    print(f"📄 Loaded {len(pages)} pages")

    embeddings = get_embeddings()

#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=800,
#         chunk_overlap=50,
#     )
    splitter = SemanticChunker(
        embeddings,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=97,  # legal-doc optimized
    )

    chunks = splitter.split_documents(pages)
    print(f"✂️ Created {len(chunks)} semantic legal chunks")

    db = Chroma(
        persist_directory=DB_PATH,
        collection_name=collection_name,
        embedding_function=embeddings,
    )

    db.add_documents(chunks)
    print("✅ Legal document indexed successfully")

def load_collection(collection_name):
    print(f"📂 [CHROMA] Loading collection: {collection_name}")

    return Chroma(
        persist_directory=DB_PATH,
        collection_name=collection_name,
        embedding_function=get_embeddings(),
    )


from langchain_core.messages import (
    SystemMessage, HumanMessage, AIMessage
)

def ask_question_stream(collection_names, query, history):
    # Support both single collection (string) and multiple collections (list)
    if isinstance(collection_names, str):
        collection_names = [collection_names]
    
    print(f"🔍 [ASK] Searching {len(collection_names)} collection(s): {collection_names}")
    
    all_docs = []
    for collection_name in collection_names:
        db = load_collection(collection_name)
        docs = db.similarity_search(query, k=3)
        all_docs.extend(docs)
        print(f"   📄 Found {len(docs)} docs in {collection_name}")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_docs = []
    for doc in all_docs:
        content_hash = hash(doc.page_content)
        if content_hash not in seen:
            seen.add(content_hash)
            unique_docs.append(doc)
    
    print(f"✂️ [ASK] Total unique docs: {len(unique_docs)}")
    context = "\n\n".join(d.page_content for d in unique_docs[:10])

    system_prompt = f"""
You are a helpful assistant.
Answer ONLY from the context below.

CONTEXT:
{context}
"""

    messages = [SystemMessage(content=system_prompt)]

    for m in history:
        if m["role"] == "user":
            messages.append(HumanMessage(content=m["content"]))
        elif m["role"] == "assistant":
            messages.append(AIMessage(content=m["content"]))

    messages.append(HumanMessage(content=query))

    for chunk in model.stream(messages):
        if chunk.content:
            yield chunk.content
