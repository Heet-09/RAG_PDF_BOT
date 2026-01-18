# backend/chat_history.py
from db import SessionLocal
from models import Conversation, Message
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()

model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.7,
    max_retries=3,
)

import json

def get_or_create_conversation(user_id: int, collections: list[str]) -> int:
    pdf_json = json.dumps(sorted(collections))

    db = SessionLocal()
    try:
        convo = (
            db.query(Conversation)
            .filter(
                Conversation.user_id == user_id,
                Conversation.pdf_names == pdf_json
            )
            .with_for_update()
            .first()
        )

        if not convo:
            convo = Conversation(
                user_id=user_id,
                pdf_names=pdf_json
            )
            db.add(convo)
            db.commit()
            db.refresh(convo)

        return convo.id
    finally:
        db.close()




def save_message(conversation_id: int, role: str, content: str):
    db = SessionLocal()
    try:
        db.add(Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        ))
        db.commit()
    finally:
        db.close()


def get_langchain_messages(conversation_id: int, limit: int = 6):
    db = SessionLocal()
    messages = (
        db.query(Message)
        .filter_by(conversation_id=conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .all()
    )
    db.close()

    messages.reverse()
    return [{"role": m.role, "content": m.content} for m in messages]


def get_summary(conversation_id):
    db = SessionLocal()
    row = db.execute(
        text("SELECT summary FROM conversation_summaries WHERE conversation_id = :id"),
        {"id": conversation_id}
    ).fetchone()

    db.close()
    return row[0] if row else None


def save_summary(conversation_id, summary):
    db = SessionLocal()
    db.execute(
        """
        INSERT INTO conversation_summaries (conversation_id, summary)
        VALUES (:id, :summary)
        ON DUPLICATE KEY UPDATE summary=:summary
        """,
        {"id": conversation_id, "summary": summary}
    )
    db.commit()
    db.close()

def maybe_update_summary(conversation_id):
    history = get_langchain_messages(conversation_id, limit=12)

    if len(history) < 12:
        return

    prompt = f"""
    Summarize the agreement discussed so far.
    {history}
    """

    response = model.invoke(prompt)
    save_summary(conversation_id, response.content)
