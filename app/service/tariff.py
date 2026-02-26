from uuid import UUID
from typing import Sequence

from app.core.error import TariffNotFound
from app.repo.tariff import TariffRepository
from app.schema.tariff import TariffCreate, TariffUpdate
from app.models.tariff import Tariff


class TariffService:
    def __init__(self, repo: TariffRepository):
        self.repo = repo

    async def create_tariff(self, payload: TariffCreate) -> Tariff:
        return await self.repo.create(payload)

    async def get_tariffs(self) -> Sequence[Tariff]:
        return await self.repo.get_all()

    async def get_tariff_by_id(self, tariff_id: UUID) -> Tariff:
        tariff = await self.repo.get_by_id(tariff_id)
        if not tariff:
            raise TariffNotFound()
        return tariff

    async def update_tariff(self, tariff_id: UUID, payload: TariffUpdate) -> Tariff:
        db_tariff = await self.get_tariff_by_id(tariff_id)
        return await self.repo.update(db_tariff, payload)

    async def delete_tariff(self, tariff_id: UUID) -> None:
        db_tariff = await self.get_tariff_by_id(tariff_id)
        await self.repo.delete(db_tariff)
