import os
import logging
import json
import torch
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from TTS.api import TTS
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer
from app.core.config import settings
from app.db.models.voice import VoiceModel, VoiceSample
from app.services.storage import StorageService
from app.core.logging import get_logger

logger = get_logger(__name__)

class VoiceCloningService:
    def __init__(self):
        self.storage_service = StorageService()
        self.device = settings.VOICE_CLONE_DEVICE
        self.model = None
        self.synthesizer = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the YourTTS model and synthesizer."""
        try:
            # Initialize model manager
            manager = ModelManager()
            
            # Get model info
            model_path = manager.download_model(settings.VOICE_CLONE_MODEL)
            config_path = os.path.join(model_path, "config.json")
            
            # Load model
            self.model = TTS(model_path=model_path, config_path=config_path).to(self.device)
            
            # Initialize synthesizer
            self.synthesizer = Synthesizer(
                tts_checkpoint=model_path,
                tts_config_path=config_path,
                use_cuda=self.device == "cuda"
            )
            
            logger.info("YourTTS model and synthesizer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize YourTTS model: {str(e)}")
            raise

    async def train_model(self, model_id: int, db) -> Dict:
        """
        Train a voice model using uploaded samples.
        
        Args:
            model_id: ID of the voice model to train
            db: Database session
            
        Returns:
            Dict containing training status and metrics
        """
        try:
            # Get model and samples
            model = db.query(VoiceModel).filter(VoiceModel.id == model_id).first()
            if not model:
                raise ValueError(f"Model {model_id} not found")

            samples = db.query(VoiceSample).filter(VoiceSample.model_id == model_id).all()
            if len(samples) < 5:
                raise ValueError("At least 5 voice samples are required for training")

            # Update model status
            model.status = "training"
            db.commit()

            # Prepare training data
            training_data = []
            for sample in samples:
                audio_path = sample.file_path
                if not os.path.exists(audio_path):
                    logger.warning(f"Sample file not found: {audio_path}")
                    continue
                
                training_data.append({
                    "audio_path": audio_path,
                    "text": sample.text or "",
                    "emotion": sample.emotion or "neutral"
                })

            # Train model
            logger.info(f"Starting training for model {model_id} with {len(training_data)} samples")
            
            # Extract speaker embeddings
            speaker_embeddings = []
            for data in training_data:
                # Load audio
                audio = self.synthesizer.load_audio(data["audio_path"])
                
                # Extract embedding
                embedding = self.model.speaker_encoder(torch.from_numpy(audio).to(self.device))
                speaker_embeddings.append(embedding)
            
            # Average embeddings
            speaker_embedding = torch.mean(torch.stack(speaker_embeddings), dim=0)
            
            # Save model checkpoint
            checkpoint_path = os.path.join(
                settings.STORAGE_DIR,
                "models",
                f"model_{model_id}_checkpoint.pt"
            )
            torch.save({
                "speaker_embedding": speaker_embedding,
                "model_id": model_id,
                "created_at": datetime.utcnow(),
                "samples_used": len(training_data)
            }, checkpoint_path)
            
            # Update model status and save checkpoint
            model.status = "ready"
            model.model_path = checkpoint_path
            model.updated_at = datetime.utcnow()
            db.commit()

            return {
                "status": "success",
                "message": "Model trained successfully",
                "metrics": {
                    "samples_used": len(training_data),
                    "training_time": "X minutes",  # Replace with actual time
                    "model_size": os.path.getsize(checkpoint_path) / (1024 * 1024)  # Size in MB
                }
            }

        except Exception as e:
            logger.error(f"Error training model {model_id}: {str(e)}")
            model.status = "failed"
            db.commit()
            raise

    async def generate_speech(self, model_id: int, text: str, db) -> str:
        """
        Generate speech from text using the trained model.
        
        Args:
            model_id: ID of the voice model to use
            text: Text to convert to speech
            db: Database session
            
        Returns:
            Path to the generated audio file
        """
        try:
            # Get model
            model = db.query(VoiceModel).filter(VoiceModel.id == model_id).first()
            if not model:
                raise ValueError(f"Model {model_id} not found")
            
            if model.status != "ready":
                raise ValueError(f"Model {model_id} is not ready for generation")

            # Load model checkpoint
            checkpoint = torch.load(model.model_path)
            speaker_embedding = checkpoint["speaker_embedding"]

            # Generate speech
            logger.info(f"Generating speech for model {model_id}")
            
            # Process text
            wav = self.synthesizer.tts(
                text=text,
                speaker_embedding=speaker_embedding,
                language="en"
            )
            
            # Save generated audio
            output_path = os.path.join(
                settings.STORAGE_DIR,
                "generated",
                f"generated_{model_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.wav"
            )
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save audio
            self.synthesizer.save_wav(wav, output_path)
            
            return output_path

        except Exception as e:
            logger.error(f"Error generating speech for model {model_id}: {str(e)}")
            raise

    async def cleanup_old_models(self, db) -> Dict:
        """
        Clean up old models and samples.
        
        Args:
            db: Database session
            
        Returns:
            Dict containing cleanup statistics
        """
        try:
            # Get old models (older than 30 days)
            old_models = db.query(VoiceModel).filter(
                VoiceModel.updated_at < datetime.utcnow() - timedelta(days=settings.MODEL_CLEANUP_DAYS)
            ).all()

            # Get old samples (older than 7 days)
            old_samples = db.query(VoiceSample).filter(
                VoiceSample.created_at < datetime.utcnow() - timedelta(days=settings.SAMPLE_CLEANUP_DAYS)
            ).all()

            # Delete old files
            deleted_models = 0
            deleted_samples = 0

            for model in old_models:
                try:
                    if os.path.exists(model.model_path):
                        os.remove(model.model_path)
                    db.delete(model)
                    deleted_models += 1
                except Exception as e:
                    logger.error(f"Error deleting model {model.id}: {str(e)}")

            for sample in old_samples:
                try:
                    if os.path.exists(sample.file_path):
                        os.remove(sample.file_path)
                    db.delete(sample)
                    deleted_samples += 1
                except Exception as e:
                    logger.error(f"Error deleting sample {sample.id}: {str(e)}")

            db.commit()

            return {
                "status": "success",
                "deleted_models": deleted_models,
                "deleted_samples": deleted_samples
            }

        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            raise

    async def check_storage_quota(self, user_id: int, db) -> Dict:
        """
        Check storage usage against quota.
        
        Args:
            user_id: ID of the user to check
            db: Database session
            
        Returns:
            Dict containing storage usage statistics
        """
        try:
            # Get user's models and samples
            models = db.query(VoiceModel).filter(VoiceModel.user_id == user_id).all()
            samples = db.query(VoiceSample).filter(
                VoiceSample.model_id.in_([m.id for m in models])
            ).all()

            # Calculate storage usage
            model_size = sum(os.path.getsize(m.model_path) for m in models if os.path.exists(m.model_path))
            sample_size = sum(os.path.getsize(s.file_path) for s in samples if os.path.exists(s.file_path))

            # Check against quotas
            model_quota = settings.MODEL_STORAGE_QUOTA
            sample_quota = settings.SAMPLE_STORAGE_QUOTA

            return {
                "model_usage": model_size,
                "model_quota": model_quota,
                "sample_usage": sample_size,
                "sample_quota": sample_quota,
                "model_quota_percent": (model_size / model_quota) * 100,
                "sample_quota_percent": (sample_size / sample_quota) * 100
            }

        except Exception as e:
            logger.error(f"Error checking storage quota for user {user_id}: {str(e)}")
            raise 