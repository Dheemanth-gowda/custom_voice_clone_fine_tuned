from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings

# Create Base class
Base = declarative_base()

# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base
from app.db.models.user import User
from app.db.models.voice import VoiceModel, VoiceSample

# Create engine with check_same_thread=False for SQLite
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Allow multiple threads
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 