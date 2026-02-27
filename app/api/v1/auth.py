from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.dependency import get_user_service, get_auth_service
from app.core.error import ExternalAuthError
from app.schema.auth import (
    RegisterOut,
    RegisterIn,
    LoginIn,
    LoginOut,
    VerifyEmailIn,
    VerifyEmailOut,
    RefreshIn, GoogleAuthLink
)
from app.service.auth import AuthService
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


@router.get("/google/login", response_model=GoogleAuthLink)
async def google_login_link(
    service: AuthService = Depends(get_auth_service)
) -> GoogleAuthLink:
    return GoogleAuthLink(url=service.get_google_auth_url())


@router.get("/google/callback", response_model=LoginOut)
async def google_callback(
    code: Optional[str] = Query(None),
    service: AuthService = Depends(get_auth_service)
) -> LoginOut:
    if not code:
        raise ExternalAuthError()
    return await service.authenticate_google(code)


@router.post("/refresh", response_model=LoginOut)
async def refresh(
    payload: RefreshIn,
    service: UserService = Depends(get_user_service)
) -> LoginOut:
    return await service.refresh_tokens(payload)
