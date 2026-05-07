from fastapi import HTTPException, status


class AppBaseError(Exception):
    status_code: int = status.HTTP_400_BAD_REQUEST
    detail: str = "Сервисная ошибка"

    def http(self) -> HTTPException:
        return HTTPException(
            status_code=self.status_code,
            detail=self.detail
        )


class UserAlreadyExistsError(AppBaseError):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Пользователь с такой почтой уже существует"


class InvalidCredentialsError(AppBaseError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный логин или пароль"


class InvalidVerificationCodeError(AppBaseError):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Неверный код подтверждения"


class TokenExpiredError(AppBaseError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Срок действия токена истек"


class InvalidTokenError(AppBaseError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Невалидный токен"


class TariffNotFound(AppBaseError):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Такого тарифа не существует"


class ExternalAuthError(AppBaseError):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Ошибка аутентификации через внешний сервис"


class PermissionDeniedError(AppBaseError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Требуются права администратора"


class EmailAlreadyVerifiedError(AppBaseError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Верификация уже пройдена"


class UserNotFoundError(AppBaseError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Пользователь с таким email не зарегистрирован"