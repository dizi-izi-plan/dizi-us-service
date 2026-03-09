from fastapi import APIRouter, Depends

from app.core.dependency import get_user_service
from app.schema.auth import (
    RegisterOut,
    RegisterIn,
    LoginIn,
    LoginOut,
    VerifyEmailIn,
    VerifyEmailOut,
    RefreshIn, PasswordResetRequestIn, PasswordResetConfirmIn
)
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
