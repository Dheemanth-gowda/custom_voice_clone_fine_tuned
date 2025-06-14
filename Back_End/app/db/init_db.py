from sqlalchemy import create_engine
from app.core.config import settings
from app.db.base import Base
from app.db.models.user import User
from app.db.models.voice import VoiceModel, VoiceSample

def init_db():
    """Initialize the database by creating all tables."""
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Creating database tables...")
    init_db()
    print("Database tables created successfully!") 