from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class VoiceModel(Base):
    __tablename__ = "voice_models"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    model_path = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, training, completed, failed
    parameters = Column(JSON)  # Store model parameters and configuration
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="voice_models")
    samples = relationship("VoiceSample", back_populates="model")

class VoiceSample(Base):
    __tablename__ = "voice_samples"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("voice_models.id"), nullable=False)
    file_path = Column(String, nullable=False)
    duration = Column(Float)  # Duration in seconds
    sample_rate = Column(Integer)
    emotion = Column(String)  # Emotion label if applicable
    text = Column(String)  # Transcribed text
    extra_metadata = Column(JSON)  # Additional metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    model = relationship("VoiceModel", back_populates="samples") 