from fastapi import Depends

from app.core.security import get_current_user
from app.core.error import PermissionDeniedError
from app.schema.mixin import UserIdAdminMixin


async def admin_required(
    current_user: UserIdAdminMixin = Depends(get_current_user),
) -> None:
    if not current_user.is_admin:
        raise PermissionDeniedError("Требуются права администратора")
