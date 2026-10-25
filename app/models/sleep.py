from datetime import date, datetime, time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.users import User
from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.users import User

class SleepEntry(Base):
    __tablename__ = "sleep_entries"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "sleep_date",
            name="uq_sleep_entries_user_date",
        ),
        CheckConstraint(
            "duration_minutes > 0 AND duration_minutes <= 1080",
            name="ck_sleep_entries_duration",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Дата пробуждения, к которой относится запись.
    sleep_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    bedtime: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    wake_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    # Рассчитывается сервером, не принимается напрямую от клиента.
    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    note: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    user: Mapped["User"] = relationship(
    "User",
    back_populates="sleep_records",
    )