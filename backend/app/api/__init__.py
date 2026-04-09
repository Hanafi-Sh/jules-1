from fastapi import APIRouter
from app.api.endpoints import generation
from app.api.endpoints import progress
from app.api.endpoints import jobs

api_router = APIRouter()
api_router.include_router(generation.router, prefix="/generate", tags=["generation"])
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
