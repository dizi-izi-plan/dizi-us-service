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
    RefreshIn, VerifyEmailV2In
)
from app.core.error import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    InvalidVerificationCodeError,
    InvalidTokenError
)
from app.tasks.worker import (
    send_verification_email,
    confirm_email_task,
    confirm_email_task_v2,
    send_verification_email_v2
)
from app.core.redis_conf import redis_service


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

        user = await self.repo.save_user(user)
        await send_verification_email.kiq(data.email, user.id)

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

        return VerifyEmailOut(message="Email успешно подтвержден")

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
