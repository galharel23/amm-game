# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()

# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql://{os.getenv('DATABASE_USER','ammuser')}:{os.getenv('DATABASE_PASSWORD','ammpassword')}@{os.getenv('DATABASE_HOST','localhost')}:{os.getenv('DATABASE_PORT','5432')}/{os.getenv('DATABASE_NAME','amm_db')}")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True to log SQL queries
    pool_size=10,
    max_overflow=20,
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    """
    Dependency for FastAPI to inject database session into route handlers.
    
    Usage in routes:
        @router.get("/pools")
        def get_pools(db: Session = Depends(get_db)):
            return db.query(Pool).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables in the database."""
    from app.models import Base
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Drop all tables from the database (use with caution!)."""
    from app.models import Base
    Base.metadata.drop_all(bind=engine)
