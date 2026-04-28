from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schema.mixin import UserIdAdminMixin
from app.schema.subscription import SubscriptionShortRead
from app.core.dependency import get_subscription_service
from app.service.subscription import SubscriptionService

router = APIRouter()


@router.get("/my/active", response_model=SubscriptionShortRead | None)
async def get_my_active_subscription(
    current_user: UserIdAdminMixin = Depends(get_current_user),
    service: SubscriptionService = Depends(get_subscription_service)
):
    return await service.get_active_subscription(current_user.id)
