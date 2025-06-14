from fastapi import APIRouter
from app.api.v1.endpoints import voice, users, auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(voice.router, prefix="/voice-clone", tags=["voice-clone"]) 