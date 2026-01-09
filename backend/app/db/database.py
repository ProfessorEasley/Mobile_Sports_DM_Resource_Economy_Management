from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.app.models import Base



# For demo/testing, use file-based SQLite DB. Replace with PostgreSQL URI in production.
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables at startup (for app)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
