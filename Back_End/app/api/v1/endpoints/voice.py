from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict
from app.api.deps import get_current_user
from app.db.base import get_db
from app.db.models.user import User
from app.db.models.voice import VoiceModel as VoiceModelDB, VoiceSample as VoiceSampleDB
from app.schemas.voice import (
    VoiceModel,
    VoiceModelCreate,
    VoiceModelUpdate,
    VoiceSample,
    VoiceSampleCreate,
)
from app.services.voice import create_voice_model, add_voice_sample
import os
from app.core.config import settings
from app.services.voice_cloning import VoiceCloningService, BackgroundTaskService
from app.services.text_processing import TextProcessingService
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/models", response_model=VoiceModel)
def create_model(
    *,
    db: Session = Depends(get_db),
    model_in: VoiceModelCreate,
    current_user: User = Depends(get_current_user),
) -> VoiceModel:
    """
    Create a new voice model.
    """
    return create_voice_model(db, user_id=current_user.id, model_in=model_in)

@router.get("/models", response_model=List[VoiceModel])
def list_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> List[VoiceModel]:
    """
    List all voice models for the current user.
    """
    return db.query(VoiceModelDB).filter(
        VoiceModelDB.user_id == current_user.id
    ).offset(skip).limit(limit).all()

@router.post("/models/{model_id}/samples", response_model=VoiceSample)
async def upload_sample(
    *,
    db: Session = Depends(get_db),
    model_id: int,
    audio_file: UploadFile = File(...),
    emotion: str = None,
    text: str = None,
    current_user: User = Depends(get_current_user),
) -> VoiceSample:
    """
    Upload a new voice sample for a model.
    """
    # Verify model ownership
    model = db.query(VoiceModelDB).filter(
        VoiceModelDB.id == model_id,
        VoiceModelDB.user_id == current_user.id
    ).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice model not found",
        )
    
    # Save uploaded file
    file_path = os.path.join(
        settings.AUDIO_DIR,
        "raw",
        f"sample_{model_id}_{audio_file.filename}"
    )
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "wb") as f:
        content = await audio_file.read()
        f.write(content)
    
    # Create sample
    sample_in = VoiceSampleCreate(
        emotion=emotion,
        text=text,
    )
    return add_voice_sample(
        db,
        model_id=model_id,
        sample_in=sample_in,
        audio_path=file_path,
    )

@router.get("/models/{model_id}/samples", response_model=List[VoiceSample])
def list_samples(
    *,
    db: Session = Depends(get_db),
    model_id: int,
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> List[VoiceSample]:
    """
    List all samples for a voice model.
    """
    # Verify model ownership
    model = db.query(VoiceModelDB).filter(
        VoiceModelDB.id == model_id,
        VoiceModelDB.user_id == current_user.id
    ).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice model not found",
        )
    
    return db.query(VoiceSampleDB).filter(
        VoiceSampleDB.model_id == model_id
    ).offset(skip).limit(limit).all()

@router.post("/models/{model_id}/train", response_model=Dict)
async def train_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Train a voice model using uploaded samples.
    """
    try:
        voice_service = VoiceCloningService()
        background_service = BackgroundTaskService()
        
        # Check if model exists and belongs to user
        model = db.query(VoiceModel).filter(
            VoiceModel.id == model_id,
            VoiceModel.user_id == current_user.id
        ).first()
        
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Schedule training
        task = background_service.schedule_training(model_id)
        
        return {
            "status": "training_started",
            "task_id": task.id,
            "message": "Model training has been scheduled"
        }
    except Exception as e:
        logger.error(f"Error scheduling model training: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/models/{model_id}/generate", response_model=Dict)
async def generate_speech(
    model_id: int,
    text: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate speech from text using a trained model.
    """
    try:
        voice_service = VoiceCloningService()
        text_service = TextProcessingService()
        background_service = BackgroundTaskService()
        
        # Check if model exists and belongs to user
        model = db.query(VoiceModel).filter(
            VoiceModel.id == model_id,
            VoiceModel.user_id == current_user.id
        ).first()
        
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Process text
        processed_text = text_service.process_script(text)
        
        if processed_text["requires_background_processing"]:
            # Schedule background generation
            task = background_service.schedule_speech_generation(model_id, text)
            return {
                "status": "generation_started",
                "task_id": task.id,
                "message": "Speech generation has been scheduled",
                "estimated_time": "2-3 minutes per minute of audio"
            }
        else:
            # Generate immediately
            output_path = await voice_service.generate_speech(model_id, text, db)
            return {
                "status": "success",
                "output_path": output_path,
                "message": "Speech generated successfully"
            }
    except Exception as e:
        logger.error(f"Error generating speech: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/{model_id}/status", response_model=Dict)
async def get_model_status(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the status of a voice model.
    """
    try:
        model = db.query(VoiceModel).filter(
            VoiceModel.id == model_id,
            VoiceModel.user_id == current_user.id
        ).first()
        
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        return {
            "id": model.id,
            "name": model.name,
            "status": model.status,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
            "samples_count": db.query(VoiceSample).filter(VoiceSample.model_id == model_id).count()
        }
    except Exception as e:
        logger.error(f"Error getting model status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/storage/quota", response_model=Dict)
async def get_storage_quota(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get storage usage and quota information.
    """
    try:
        voice_service = VoiceCloningService()
        quota_info = await voice_service.check_storage_quota(current_user.id, db)
        
        return {
            "user_id": current_user.id,
            "model_usage_mb": quota_info["model_usage"] / (1024 * 1024),
            "model_quota_mb": quota_info["model_quota"] / (1024 * 1024),
            "sample_usage_mb": quota_info["sample_usage"] / (1024 * 1024),
            "sample_quota_mb": quota_info["sample_quota"] / (1024 * 1024),
            "model_quota_percent": quota_info["model_quota_percent"],
            "sample_quota_percent": quota_info["sample_quota_percent"]
        }
    except Exception as e:
        logger.error(f"Error getting storage quota: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup", response_model=Dict)
async def cleanup_storage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger storage cleanup.
    """
    try:
        voice_service = VoiceCloningService()
        background_service = BackgroundTaskService()
        
        # Schedule cleanup
        task = background_service.schedule_cleanup()
        
        return {
            "status": "cleanup_started",
            "task_id": task.id,
            "message": "Storage cleanup has been scheduled"
        }
    except Exception as e:
        logger.error(f"Error scheduling cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 