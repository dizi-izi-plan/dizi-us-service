import uuid
import datetime
from typing import Optional
from sqlalchemy import String, Boolean, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    hash_password: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )

    google_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        nullable=True
    )

    yandex_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        nullable=True
    )

    city: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    birthday: Mapped[Optional[datetime.date]] = mapped_column(
        Date,
        nullable=True
    )

    confirmed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    subscriptions = relationship(
        "Subscription",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )