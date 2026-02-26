from fastapi import APIRouter
from app.api.v2.auth import router as auth_router

v2_router = APIRouter()

v2_router.include_router(auth_router, prefix="/auth", tags=["Auth V2"])
