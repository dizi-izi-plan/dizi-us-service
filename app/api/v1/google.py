from fastapi import APIRouter, Depends, Query
from app.core.dependency import get_auth_service
from app.schema.auth import GoogleAuthLink, LoginOut
from app.service.auth import AuthService

router = APIRouter()


@router.get("/login", response_model=GoogleAuthLink)
async def google_login_link(
    service: AuthService = Depends(get_auth_service)
) -> GoogleAuthLink:
    return GoogleAuthLink(url=service.get_google_auth_url())


@router.get("/callback", response_model=LoginOut)
async def google_callback(
    code: str = Query(...),
    service: AuthService = Depends(get_auth_service)
) -> LoginOut:
    return await service.authenticate_google(code)
