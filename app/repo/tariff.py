from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tariff import Tariff
from app.schema.tariff import TariffCreate, TariffUpdate


class TariffRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, schema: TariffCreate) -> Tariff:
        new_tariff = Tariff(**schema.model_dump())
        self.session.add(new_tariff)
        await self.session.commit()
        await self.session.refresh(new_tariff)
        return new_tariff

    async def get_all(self) -> Sequence[Tariff]:
        result = await self.session.execute(select(Tariff))
        return result.scalars().all()

    async def get_by_id(self, tariff_id: UUID) -> Tariff | None:
        return await self.session.get(Tariff, tariff_id)

    async def update(self, db_tariff: Tariff, schema: TariffUpdate) -> Tariff:
        update_data = schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_tariff, key, value)
        await self.session.commit()
        await self.session.refresh(db_tariff)
        return db_tariff

    async def delete(self, db_tariff: Tariff) -> None:
        await self.session.delete(db_tariff)
        await self.session.commit()
