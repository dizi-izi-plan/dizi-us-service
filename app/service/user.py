import uuid
import secrets
from hashlib import sha256
from pydantic import EmailStr

from app.core.logger import get_logger
from app.core.security import (
    hash_password,
    verify_password,
    create_token_pair,
    decode_refresh_token,
    decode_verification_token
)
from app.models.user import User
from app.schema.auth import (
    RegisterOut,
    RegisterIn,
    LoginIn,
    LoginOut,
    VerifyEmailIn,
    VerifyEmailOut,
    RefreshIn,
    VerifyEmailV2In
)
from app.core.error import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    InvalidVerificationCodeError,
    InvalidTokenError,
)
from app.service.mail import mail_service
from app.tasks.worker import (
    send_verification_email,
    confirm_email_task,
    confirm_email_task_v2,
    send_verification_email_v2
)
from app.core.redis_conf import redis_service

logger = get_logger(__name__)


class UserService:
    def __init__(self, repo):
        self.repo = repo

    async def register(self, data: RegisterIn) -> RegisterOut:
        existing = await self.repo.get_by_email(data.email)

        if existing:
            raise UserAlreadyExistsError()

        user = User(
            email=data.email,
            hash_password=hash_password(data.password)
        )

        await self.repo.save_user(user)
        await send_verification_email.kiq(data.email)

        return RegisterOut()

    async def register_v2(self, data: RegisterIn) -> RegisterOut:
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise UserAlreadyExistsError()

        user = User(
            email=data.email,
            hash_password=hash_password(data.password)
        )
        user = await self.repo.save_user(user)

        await send_verification_email_v2.kiq(data.email, user.id)

        return RegisterOut()

    @staticmethod
    async def verify(data: VerifyEmailIn) -> VerifyEmailOut:
        stored_code = await redis_service.get_verification_code(data.email)

        if stored_code is None or str(stored_code) != str(data.code):
            raise InvalidVerificationCodeError()

        await confirm_email_task.kiq(data.email)

        return VerifyEmailOut()

    @staticmethod
    async def verify_v2(data: VerifyEmailV2In) -> VerifyEmailOut:
        payload = decode_verification_token(data.token)
        user_id = payload.get("sub")

        if not user_id:
            raise InvalidTokenError()

        await confirm_email_task_v2.kiq(user_id)

        return VerifyEmailOut()

    async def login(self, data: LoginIn) -> LoginOut:
        user = await self.repo.get_by_email(data.email)

        if not user or not verify_password(
            data.password, str(user.hash_password)
        ):
            raise InvalidCredentialsError()

        return create_token_pair(str(user.id))

    async def refresh_tokens(self, data: RefreshIn) -> LoginOut:
        payload = decode_refresh_token(data.refresh_token)
        user_id = payload.get("sub")

        if not user_id:
            raise InvalidCredentialsError()

        user = await self.repo.get_by_id(user_id)

        if not user:
            raise InvalidCredentialsError()

        return create_token_pair(str(user.id))

    async def change_password(
        self,
        user_id: uuid.UUID,
        old_password: str,
        new_password: str
    ):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise InvalidCredentialsError("Пользователь не найден")

        if not verify_password(old_password, user.hash_password):
            raise InvalidCredentialsError("Старый пароль неверный")

        hashed_password = hash_password(new_password)

        await self.repo.update_password(user.id, hashed_password)

        return {"detail": "Пароль успешно изменен"}

    async def request_password_reset(self, email: EmailStr):
        user = await self.repo.get_by_email(email)
        if not user:
            return

        raw_token = secrets.token_urlsafe(32)
        token_hash = sha256(raw_token.encode()).hexdigest()

        await redis_service.set(f"pwd_reset:{token_hash}", str(user.id), expire=1200)

        reset_url = f"http://localhost/reset?token={raw_token}"

        await mail_service.send_password_reset_link(user.email, reset_url)

    async def confirm_password_reset(self, token: str, new_password: str):
        token_hash = sha256(token.encode()).hexdigest()
        user_id = await redis_service.get(f"pwd_reset:{token_hash}")

        if not user_id:
            raise InvalidTokenError("Неверный или просроченный токен")

        hashed_password = hash_password(new_password)

        await self.repo.update_password(user_id, hashed_password)

        await redis_service.delete(f"pwd_reset:{token_hash}")
