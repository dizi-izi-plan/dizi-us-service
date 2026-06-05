from pydantic import BaseModel, EmailStr
from app.schema.mixin import EmailMixin, PasswordMixin, CodeMixin, TokenMixin
import uuid


class RegisterIn(EmailMixin, PasswordMixin):
    pass


class RegisterOut(BaseModel):
    message: str = "Письмо для подтверждения отправлена на почту"


class VerifyEmailIn(EmailMixin, CodeMixin):
    pass


class VerifyEmailOut(BaseModel):
    message: str = "Почта подтверждена"


class LoginIn(EmailMixin, PasswordMixin):
    pass


class LoginOut(TokenMixin):
    pass


class RefreshIn(BaseModel):
    refresh_token: str = "Refresh токен"


class VerifyEmailV2In(BaseModel):
    token: str


class AuthLink(BaseModel):
    url: str


class AuthUserSchema(BaseModel):
    email: EmailStr
    sub: str
    email_verified: bool = False


class PasswordResetRequestIn(BaseModel):
    email: EmailStr


class PasswordResetConfirmIn(PasswordMixin):
    token: str


class UserRead(BaseModel):
    id: uuid.UUID
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None

    class Config:
        from_attributes = True
