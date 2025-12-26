from db import Base
from sqlalchemy import Column, BigInteger, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    collection = Column(Text)  # pdf / chroma collection
    created_at = Column(DateTime, server_default=func.now())

    messages = relationship(
        "Message",
        back_populates="conversation",
        order_by="Message.created_at"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id = Column(BigInteger, ForeignKey("conversations.id"))
    role = Column(Enum("system", "user", "assistant"))
    content = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")
