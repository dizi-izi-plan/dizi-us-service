from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.tariff import router as tariff_router

v1_router = APIRouter()

v1_router.include_router(auth_router, prefix="/auth", tags=["Auth V1"])
v1_router.include_router(tariff_router, prefix="/tariff", tags=["Tariffs V1"])
