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
    RefreshIn, PasswordResetRequestIn, PasswordResetConfirmIn
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


@router.post("/password-reset/request")
async def password_reset_request(
    payload: PasswordResetRequestIn,
    service: UserService = Depends(get_user_service)
):
    await service.request_password_reset(payload.email)
    return {"detail": "Инструкция по восстановлению пароля отправлена на почту"}


@router.post("/password-reset/confirm")
async def password_reset_confirm(
    payload: PasswordResetConfirmIn,
    service: UserService = Depends(get_user_service)
):
    await service.confirm_password_reset(payload.token, payload.password)
    return {"detail": "Пароль успешно обновлен"}


""" Временные эндпоинты для ручного тестирования is_admin методов """
import uuid
from typing import Dict, Any

@router.get("/me")
async def get_my_id(current_user: UserIdMixin = Depends(get_current_user)):
    return {"user_id": current_user.id}

@router.get("/is_admin/{user_id}")
async def get_admin_status(
    user_id: uuid.UUID,
    service: UserService = Depends(get_user_service)
):
    is_admin = await service.get_admin_status(user_id)
    return {"is_admin": is_admin}

@router.post("/set_admin_status")
async def set_admin_status(
    payload: Dict[str, Any],
    service: UserService = Depends(get_user_service)
):
    user_admin_status = await service.set_admin_status(payload["user_id"], payload["is_admin"], payload["ttl"])
    return user_admin_status

@router.post("/invalidate_admin_cache")
async def invalidate_admin_cache(
    payload: Dict[str, uuid.UUID],
    service: UserService = Depends(get_user_service)
):
    deleted = await service.invalidate_admin_cache(payload["user_id"])
    return deleted