"""
Database engine and session configuration.
Uses SQLite by default for local/dev and hackathon demo purposes.
Swap SQLALCHEMY_DATABASE_URL to a Postgres/MySQL URL for production
without changing any other file.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./hres.db"

# check_same_thread is only needed for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Called once on app startup."""
    Base.metadata.create_all(bind=engine)
