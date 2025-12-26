from db import SessionLocal
from models import Conversation, Message

def get_or_create_conversation(collection: str) -> int:
    db = SessionLocal()
    convo = db.query(Conversation).filter_by(collection=collection).first()

    if not convo:
        convo = Conversation(collection=collection)
        db.add(convo)
        db.commit()
        db.refresh(convo)

    db.close()
    return convo.id


def save_message(conversation_id: int, role: str, content: str):
    db = SessionLocal()
    msg = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    db.add(msg)
    db.commit()
    db.close()


def get_langchain_messages(conversation_id: int, limit: int = 10):
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
