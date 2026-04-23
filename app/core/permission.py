from fastapi import Depends

from app.core.security import get_current_user
from app.core.dependency import get_user_service
from app.service.user import UserService
from app.schema.mixin import UserIdMixin
from app.core.error import PermissionDeniedError


async def admin_required(
    current_user: UserIdMixin = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> None:
    is_admin = await user_service.get_admin_status(current_user.id)
    if not is_admin:
        raise PermissionDeniedError("Требуются права администратора")
