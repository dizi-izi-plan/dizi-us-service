import uuid
import datetime
from sqlalchemy import ForeignKey, Boolean, UniqueConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    __table_args__ = (
        UniqueConstraint("user_id", "is_active", name="uq_user_active_subscription"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    tariff_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tariffs.id", ondelete="CASCADE"),
        nullable=False
    )

    start_date: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    end_date: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    user = relationship("User", back_populates="subscriptions")
    tariff = relationship("Tariff", back_populates="subscriptions")
