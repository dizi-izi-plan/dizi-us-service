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
from app.schema.mixin import PasswordChangeIn, UserIdAdminMixin
from app.service.user import UserService

router = APIRouter()


@router.post("/register", response_model=RegisterOut)
async def register(
    payload: RegisterIn,
    service: UserService = Depends(get_user_service)
) -> RegisterOut:
    return await service.register(payload)


@router.post("/resend-code", response_model=RegisterOut)
async def resend_code(
    payload: RegisterIn,
    service: UserService = Depends(get_user_service)
) -> RegisterOut:
    return await service.resend_code(payload)


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
    current_user: UserIdAdminMixin = Depends(get_current_user),
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


@router.get("/me")
async def get_token_info(
    current_user: UserIdAdminMixin = Depends(get_current_user)
):
    return current_user
