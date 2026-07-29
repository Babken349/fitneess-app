from datetime import datetime, time
from typing import TYPE_CHECKING

from sqlalchemy import Integer, DateTime, Time, ForeignKey, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.user_supplements import UserSupplement


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user_supplement_id: Mapped[int | None] = mapped_column(ForeignKey("user_supplements.id"), nullable=True)

    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=понедельник, 6=воскресенье
    time_of_day: Mapped[time] = mapped_column(Time, nullable=False)     # 16:00:00
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship()
    user_supplement: Mapped["UserSupplement | None"] = relationship()