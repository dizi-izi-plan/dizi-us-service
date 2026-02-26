from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.repo.tariff import TariffRepository
from app.repo.user import UserRepository
from app.service.tariff import TariffService
from app.service.user import UserService


def get_user_service(
    session: AsyncSession = Depends(get_session),
) -> UserService:
    repo = UserRepository(session)
    return UserService(repo)


def get_tariff_service(
    session: AsyncSession = Depends(get_session),
) -> TariffService:
    repo = TariffRepository(session)
    return TariffService(repo)
