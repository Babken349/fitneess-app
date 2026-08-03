from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens" # Красивое имя таблицы во множественном числе

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    reset_token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())