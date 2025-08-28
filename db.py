from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Get database URL from environment
database_url = os.getenv("SQLALCHEMY_DATABASE_URL")

# Create engine with MySQL-specific configurations
engine = create_engine(
    database_url, # type: ignore
    pool_pre_ping=True,  # Validates connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
    echo=False           # Set to True for SQL debugging
    )


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()