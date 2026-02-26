import uuid

from app.core.error import SubscriptionNotFoundError
from app.repo.subscription import SubscriptionRepository


class SubscriptionService:
    def __init__(self, repo: SubscriptionRepository):
        self.repo = repo

    async def get_active_subscription(self, user_id: uuid.UUID):
        subscription = await self.repo.get_active_subscription_by_user_id(user_id)

        if not subscription:
            raise SubscriptionNotFoundError()

        return subscription
