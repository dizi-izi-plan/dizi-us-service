from fastapi import Depends

from app.core.security import get_current_user
from app.core.dependency import get_user_service
from app.service.user import UserService
from app.schema.mixin import UserIdMixin
from app.core.error import PermissionDeniedError


async def admin_required(
    current_user: UserIdMixin = Depends(get_current_user),
) -> None:
    if not current_user.is_admin:
        raise PermissionDeniedError("Требуются права администратора")
