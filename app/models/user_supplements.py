from datetime import datetime


from sqlalchemy import String, Integer, DateTime, ForeignKey, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.core.database import Base


class UserSupplement(Base):
    __tablename__ = "user_supplements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    supplement_id: Mapped[int] = mapped_column(
        ForeignKey("supplements.id"),
        nullable=False,
    )

    dosage: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    frequency: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    notes: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    user: Mapped["User"] = relationship(
        back_populates="supplements",
    )

    supplement: Mapped["Supplement"] = relationship()

    # обратная связь к SupplementIntake
    intakes: Mapped[list["SupplementIntake"]] = relationship(
        "SupplementIntake",
        back_populates="user_supplement",
        cascade="all, delete-orphan",
    )