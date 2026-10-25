from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Float, DateTime, ForeignKey, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.users import User


class BodyMeasurement(Base):
    __tablename__ = "body_measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
    ForeignKey("users.id", ondelete="CASCADE"),
    nullable=False,
    index=True,
    )

    chest: Mapped[float | None] = mapped_column(Float, nullable=True)
    waist: Mapped[float | None] = mapped_column(Float, nullable=True)
    hips: Mapped[float | None] = mapped_column(Float, nullable=True)
    biceps: Mapped[float | None] = mapped_column(Float, nullable=True)
    thigh: Mapped[float | None] = mapped_column(Float, nullable=True)
    forearm: Mapped[float | None] = mapped_column(Float, nullable=True)
    calf: Mapped[float | None] = mapped_column(Float, nullable=True)

    recorded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="body_measurements")