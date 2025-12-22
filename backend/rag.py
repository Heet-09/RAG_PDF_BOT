import os
import json
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage

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
    print(f"📄 [CHROMA] Loading PDF: {file_path}")

    loader = PyPDFLoader(file_path)
    pages = loader.load()
    print(f"📄 [CHROMA] Loaded {len(pages)} pages")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=50,
    )

    chunks = splitter.split_documents(pages)
    print(f"✂️ [CHROMA] Split into {len(chunks)} chunks")

    db = Chroma(
        persist_directory=DB_PATH,
        collection_name=collection_name,
        embedding_function=get_embeddings(),
    )

    db.add_documents(chunks)
    print("✅ [CHROMA] Documents added to Chroma DB")

def load_collection(collection_name):
    print(f"📂 [CHROMA] Loading collection: {collection_name}")

    return Chroma(
        persist_directory=DB_PATH,
        collection_name=collection_name,
        embedding_function=get_embeddings(),
    )

# def ask_question(collection_name, query):
#     print("❓ [RAG] Starting question answering")
#     print(f"📄 [RAG] Collection: {collection_name}")
#     print(f"❓ [RAG] Query: {query}")

#     db = load_collection(collection_name)

#     docs = db.similarity_search(query, k=3)
#     print(f"🔍 [RAG] Retrieved {len(docs)} documents")

#     if not docs:
#         print("⚠️ [RAG] No relevant documents found")
#         return "No relevant information found."

#     context = "\n\n".join(
#         f"[Page {d.metadata.get('page')}]\n{d.page_content}"
#         for d in docs
#     )

#     print("🧠 [RAG] Context constructed")

#     prompt = f"""
# You are a helpful assistant.
# Answer ONLY from the context below.
# If not present, say the information is not available.

# CONTEXT:
# {context}

# QUESTION:
# {query}
# """

#     print("🤖 [RAG] Sending prompt to LLM")
#     response = model.invoke([SystemMessage(content=prompt)])

#     print("✅ [RAG] LLM response received")
#     return response.content

def ask_question_stream(collection_name, query):
    print("🧠 [RAG-STREAM] Starting streaming RAG")

    db = load_collection(collection_name)
    docs = db.similarity_search(query, k=3)

    if not docs:
        yield "No relevant information found."
        return

    context = "\n\n".join(
        f"[Page {d.metadata.get('page')}]\n{d.page_content}"
        for d in docs
    )

    prompt = f"""
You are a helpful assistant.
Answer ONLY from the context below.
If not present, say the information is not available.

CONTEXT:
{context}

QUESTION:
{query}
"""

    print("🤖 [RAG-STREAM] Sending prompt to LLM")

    for chunk in model.stream([SystemMessage(content=prompt)]):
        if chunk.content:
            yield chunk.content
