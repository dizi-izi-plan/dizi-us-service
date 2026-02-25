import uuid
from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class Tariff(Base):
    __tablename__ = "tariffs"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    price: Mapped[int] = mapped_column(  # в копейках
        Integer,
        nullable=False
    )

    period_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    project_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    room_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    furniture_regeneration_limit: Mapped[int] = mapped_column(Integer, nullable=False)

    subscriptions = relationship("Subscription", back_populates="tariff")
