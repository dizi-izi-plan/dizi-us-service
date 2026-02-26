
from fastapi import APIRouter, Depends

from app.core.dependency import get_user_service
from app.schema.auth import (
    RegisterOut,
    RegisterIn,
    VerifyEmailOut, VerifyEmailV2In
)
from app.service.user import UserService

router = APIRouter()


@router.post("/register", response_model=RegisterOut)
async def register_v2(
    payload: RegisterIn,
    service: UserService = Depends(get_user_service)
) -> RegisterOut:
    return await service.register_v2(payload)


@router.get("/verify", response_model=VerifyEmailOut)
async def verify_email_v2(
    token: str,
    service: UserService = Depends(get_user_service)
) -> VerifyEmailOut:
    return await service.verify_v2(VerifyEmailV2In(token=token))
