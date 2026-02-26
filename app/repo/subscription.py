import uuid
import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.subscription import Subscription
from app.models.tariff import Tariff


class SubscriptionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_free_subscription(
        self,
        user_id: uuid.UUID
    ) -> Subscription | None:

        tariff_query = await self.session.execute(
            select(Tariff).where(Tariff.name == "Бесплатный")
        )
        tariff = tariff_query.scalar_one_or_none()
        if not tariff:
            return None

        start_date = datetime.datetime.now(datetime.timezone.utc)
        end_date = start_date + datetime.timedelta(days=tariff.period_days)

        new_subscription = Subscription(
            user_id=user_id,
            tariff_id=tariff.id,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )

        self.session.add(new_subscription)
        await self.session.commit()
        await self.session.refresh(new_subscription)
        return new_subscription
