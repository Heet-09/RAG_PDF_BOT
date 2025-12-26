from sqlalchemy import (
    create_engine, Column, BigInteger,
    Text, Enum, DateTime, ForeignKey, func
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = "mysql+pymysql://root:Phy$ics56@127.0.0.1:3306/chatdb"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
