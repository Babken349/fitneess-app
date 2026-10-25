from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.users import User


class StudyState(Base):
    __tablename__ = "study_states"

    __table_args__ = (
        CheckConstraint(
            "duration_minutes IS NULL OR "
            "(duration_minutes > 0 AND duration_minutes <= 720)",
            name="ck_study_states_duration",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    subject: Mapped[str] = mapped_column(
        String(100), nullable=False, server_default="",
    )

    duration_minutes: Mapped[int | None] = mapped_column(
        Integer, nullable=True,
    )

    concentration: Mapped[int] = mapped_column(Integer, nullable=False)
    energy: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fatigue: Mapped[int | None] = mapped_column(Integer, nullable=True)
    motivation: Mapped[int | None] = mapped_column(Integer, nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True,
    )

    user: Mapped["User"] = relationship(back_populates="study_states")
