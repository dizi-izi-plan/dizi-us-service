import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from pydantic import EmailStr

from app.schema.auth import GoogleUserSchema


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

    async def get_by_google_id(self, google_id: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.google_id == google_id)
        )
        return result.scalar_one_or_none()

    async def create_google_user(
        self,
        email: str,
        google_id: str,
        confirmed: bool
    ) -> User:
        user = User(
            email=email,
            google_id=google_id,
            confirmed=confirmed,
            hash_password=None
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def create_via_google(
        self,
        google_data: GoogleUserSchema
    ) -> User:
        user = User(
            email=google_data.email,
            google_id=google_data.sub,
            confirmed=google_data.email_verified,
            hash_password=None
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
