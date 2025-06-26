# app/utils/database.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import urllib

# ▶️ Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("Environment variable DATABASE_URL is required")

# Optional: handle percent-encoding in URL
# DATABASE_URL = urllib.parse.unquote_plus(DATABASE_URL)

# ▶️ Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,        # Ensures connections are checked before use
    fast_executemany=True,     # Speeds up bulk INSERTs (SQL Server)
    echo=False,                # Set True for SQL debugging
    connect_args={"timeout": 5}
)

# ▶️ Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ▶️ Base class for ORM
Base = declarative_base()

# ▶️ Dependency: provide a db session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ▶️ Optional: create tables at startup, wrapped in try/except
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError as err:
        print("⚠️ Database init failed:", err)

# ▶️ Models import (ensure all ORM classes are loaded)
from app.models.documents import Document
from app.auth.models import User
from app.models.chat import ChatHistory
