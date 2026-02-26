import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from pydantic import EmailStr


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: EmailStr) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def save_user(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def confirm_user_by_email(self, email: EmailStr) -> bool:
        result = await self.session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            user.confirmed = True
            await self.session.commit()
            return True
        return False

    async def confirm_user_by_id(self, user_id: uuid.UUID | str) -> bool:
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)

        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.confirmed = True
            await self.session.commit()
            return True
        return False
