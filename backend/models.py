#bakcned/models.py
from db import Base
from sqlalchemy import Column, BigInteger, Text, Enum, DateTime, ForeignKey,Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(Text, unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    conversations = relationship("Conversation", back_populates="user")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    pdf_names = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    is_archived = Column(Boolean, default=False)

    user = relationship("User", back_populates="conversations")

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

class UserPDF(Base):
    __tablename__ = "user_pdfs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    collection_name = Column(Text, nullable=False)
    filename = Column(Text, nullable=False)

    created_at = Column(DateTime, server_default=func.now())
