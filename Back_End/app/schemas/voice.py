from pydantic import BaseModel, constr
from typing import Optional, Dict, Any
from datetime import datetime

class VoiceModelBase(BaseModel):
    name: constr(min_length=1, max_length=100)
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class VoiceModelCreate(VoiceModelBase):
    pass

class VoiceModelUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=100)] = None
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class VoiceModelInDBBase(VoiceModelBase):
    id: int
    user_id: int
    model_path: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class VoiceModel(VoiceModelInDBBase):
    pass

class VoiceSampleBase(BaseModel):
    emotion: Optional[str] = None
    text: Optional[str] = None
    voice_metadata: Optional[Dict[str, Any]] = None

class VoiceSampleCreate(VoiceSampleBase):
    pass

class VoiceSampleUpdate(BaseModel):
    emotion: Optional[str] = None
    text: Optional[str] = None
    voice_metadata: Optional[Dict[str, Any]] = None

class VoiceSampleInDBBase(VoiceSampleBase):
    id: int
    model_id: int
    file_path: str
    duration: Optional[float] = None
    sample_rate: Optional[int] = None
    created_at: datetime

    class Config:
        orm_mode = True

class VoiceSample(VoiceSampleInDBBase):
    pass 