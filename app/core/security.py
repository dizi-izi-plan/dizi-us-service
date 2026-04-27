from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.schema.auth import LoginOut
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from app.repo.user import UserRepository
from app.core.config import settings
from jose import jwt, JWTError, ExpiredSignatureError

from app.schema.mixin import UserIdMixin
from app.core.error import InvalidCredentialsError, InvalidTokenError, TokenExpiredError

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(data: dict, expires_delta: timedelta) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    payload["exp"] = expire
    return jwt.encode(
        payload,
        settings.jwt.secret,
        algorithm=settings.jwt.algorithm
    )


def create_access_token(user_id: str, is_admin: bool) -> str:
    return _create_token(
        {"sub": user_id, "typ": "access", "is_admin": is_admin},
        timedelta(minutes=settings.jwt.access_expire_minutes)
    )


def create_refresh_token(user_id: str) -> str:
    return _create_token(
        {"sub": user_id, "typ": "refresh"},
        timedelta(days=settings.jwt.refresh_expire_days)
    )


def create_token_pair(user_id: str, is_admin: bool) -> LoginOut:
    return LoginOut(
        access_token=create_access_token(user_id, is_admin),
        refresh_token=create_refresh_token(user_id),
        token_type="bearer"
    )


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token=token,
            key=settings.jwt.secret,
            algorithms=[settings.jwt.algorithm]
        )
        if payload.get("typ") != "access":
            raise InvalidTokenError()
        return payload
    except ExpiredSignatureError:
        raise TokenExpiredError()
    except JWTError:
        raise InvalidTokenError()


def decode_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token=token,
            key=settings.jwt.secret,
            algorithms=[settings.jwt.algorithm]
        )
        if payload.get("typ") != "refresh":
            raise InvalidTokenError()
        return payload
    except ExpiredSignatureError:
        raise TokenExpiredError()
    except JWTError:
        raise InvalidTokenError()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> UserIdMixin:
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    is_admin = payload.get("is_admin")
    if not user_id:
        raise InvalidCredentialsError()

    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if not user:
        raise InvalidCredentialsError()

    return UserIdMixin(id=user.id, is_admin=is_admin)


def create_verification_token(user_id: str) -> str:
    return _create_token(
        {"sub": user_id, "typ": "email_confirmation"},
        timedelta(hours=24)
    )


def decode_verification_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, settings.jwt.secret, algorithms=[settings.jwt.algorithm]
        )
        if payload.get("typ") != "email_confirmation":
            raise InvalidTokenError()
        return payload
    except (JWTError, ExpiredSignatureError):
        raise InvalidTokenError()
