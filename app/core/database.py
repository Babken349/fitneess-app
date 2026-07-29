from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings  # Берем настройки из нашего конфига!

# Создаем движок, используя URL из настроек
engine = create_engine(settings.DATABASE_URL) # ВАЖНО: добавь DATABASE_URL в класс Settings и в .env файл!

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Новый стиль SQLAlchemy 2.0
class Base(DeclarativeBase):
    pass