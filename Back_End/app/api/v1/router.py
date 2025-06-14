from fastapi import APIRouter
from app.api.v1.endpoints import auth, voice

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(voice.router, prefix="/voice", tags=["voice"]) 