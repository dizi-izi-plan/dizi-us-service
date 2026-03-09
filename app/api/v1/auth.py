from fastapi import APIRouter, Depends

from app.core.dependency import get_user_service
from app.core.security import get_current_user
from app.schema.auth import (
    RegisterOut,
    RegisterIn,
    LoginIn,
    LoginOut,
    VerifyEmailIn,
    VerifyEmailOut,
    RefreshIn
)
from app.schema.mixin import PasswordChangeIn, UserIdMixin
from app.service.user import UserService

router = APIRouter()


@router.post("/register", response_model=RegisterOut)
async def register(
    payload: RegisterIn,
    service: UserService = Depends(get_user_service)
) -> RegisterOut:
    return await service.register(payload)


@router.post("/verify", response_model=VerifyEmailOut)
async def verify(
    payload: VerifyEmailIn,
    service: UserService = Depends(get_user_service)
) -> VerifyEmailOut:
    return await service.verify(payload)


@router.post("/login", response_model=LoginOut)
async def login(
    payload: LoginIn,
    service: UserService = Depends(get_user_service)
) -> LoginOut:
    return await service.login(payload)


@router.post("/refresh", response_model=LoginOut)
async def refresh(
    payload: RefreshIn,
    service: UserService = Depends(get_user_service)
) -> LoginOut:
    return await service.refresh_tokens(payload)


@router.post("/password-change")
async def password_change(
    payload: PasswordChangeIn,
    current_user: UserIdMixin = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    return await service.change_password(
        user_id=current_user.id,
        old_password=payload.old_password,
        new_password=payload.new_password
    )
