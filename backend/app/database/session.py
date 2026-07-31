from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text
from app.core.config import settings


def _create_engine():
    if settings.DATABASE_URL.startswith("postgresql"):
        try:
            engine = create_engine(
                settings.DATABASE_URL,
                pool_pre_ping=True,
                connect_args={"connect_timeout": 5, "sslmode": "require"},
            )
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}")
            print("Hint: If testing connection, use a valid PostgreSQL URL like 'postgresql://postgres:password@host:5432/database'")
            print("For local testing, consider using SQLite: sqlite:///ecocity.db")
            return None

    # For development/testing, allow SQLite even if DATABASE_URL is not set
    try:
        fallback_url = "sqlite:///ecocity.db"
        engine = create_engine(fallback_url, connect_args={"check_same_thread": False})
        print(f"Warning: Using SQLite fallback for local development: {fallback_url}")
        return engine
    except Exception as e:
        raise ValueError(f"Failed to create fallback SQLite engine: {e}")


engine = _create_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
