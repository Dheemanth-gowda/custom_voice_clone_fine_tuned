import os
import librosa
import soundfile as sf
import numpy as np
from typing import Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models.voice import VoiceModel, VoiceSample
from app.schemas.voice import VoiceModelCreate, VoiceSampleCreate

def process_audio(
    audio_path: str,
    target_sr: int = 22050,
    normalize: bool = True,
    trim_silence: bool = True,
) -> Tuple[np.ndarray, int]:
    """
    Process audio file: load, resample, normalize, and trim silence.
    """
    # Load audio
    audio, sr = librosa.load(audio_path, sr=target_sr)
    
    # Normalize
    if normalize:
        audio = librosa.util.normalize(audio)
    
    # Trim silence
    if trim_silence:
        audio, _ = librosa.effects.trim(audio, top_db=20)
    
    return audio, sr

def extract_features(
    audio: np.ndarray,
    sr: int,
) -> Dict[str, Any]:
    """
    Extract audio features for voice cloning.
    """
    # Mel spectrogram
    mel_spec = librosa.feature.melspectrogram(
        y=audio,
        sr=sr,
        n_mels=80,
        fmax=8000
    )
    
    # Fundamental frequency
    f0, voiced_flag, voiced_probs = librosa.pyin(
        audio,
        fmin=librosa.note_to_hz('C2'),
        fmax=librosa.note_to_hz('C7')
    )
    
    # Energy
    energy = librosa.feature.rms(y=audio)[0]
    
    return {
        'mel_spectrogram': mel_spec.tolist(),
        'f0': f0.tolist() if f0 is not None else None,
        'energy': energy.tolist(),
        'duration': len(audio) / sr
    }

def save_audio(
    audio: np.ndarray,
    sr: int,
    file_path: str,
) -> None:
    """
    Save audio array to file.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    sf.write(file_path, audio, sr)

def create_voice_model(
    db: Session,
    *,
    user_id: int,
    model_in: VoiceModelCreate,
) -> VoiceModel:
    """
    Create a new voice model.
    """
    model_path = str(settings.MODELS_DIR / f"model_{user_id}_{model_in.name}")
    
    db_model = VoiceModel(
        user_id=user_id,
        name=model_in.name,
        description=model_in.description,
        model_path=model_path,
        parameters=model_in.parameters,
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

def add_voice_sample(
    db: Session,
    *,
    model_id: int,
    sample_in: VoiceSampleCreate,
    audio_path: str,
) -> VoiceSample:
    """
    Add a new voice sample to a model.
    """
    # Process audio
    audio, sr = process_audio(audio_path)
    
    # Extract features
    features = extract_features(audio, sr)
    
    # Save processed audio
    processed_path = str(settings.AUDIO_DIR / "processed" / f"sample_{model_id}_{os.path.basename(audio_path)}")
    save_audio(audio, sr, processed_path)
    
    # Create sample record
    db_sample = VoiceSample(
        model_id=model_id,
        file_path=processed_path,
        duration=features['duration'],
        sample_rate=sr,
        emotion=sample_in.emotion,
        text=sample_in.text,
        extra_metadata={**(sample_in.voice_metadata or {}), **features}
    )
    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)
    return db_sample 