#backend/db.py
import os
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, BigInteger,
    Text, Enum, DateTime, ForeignKey, func
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
