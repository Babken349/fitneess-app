from sqlalchemy import Column, Integer, String, Float, String, DateTime, func
from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column

class Supplement(Base):
    __tablename__ = "supplements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=True)
    