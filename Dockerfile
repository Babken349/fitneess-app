# syntax=docker/dockerfile:1
# Dockerfile для backend (только локальная разработка, без production-настроек)

# ---------- базовый этап: Python и зависимости ----------
FROM python:3.11-slim AS base

# Не писать .pyc-файлы и сразу выводить логи (без буфера)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Обычный пользователь вместо root; каталог /app принадлежит ему
RUN useradd --create-home --uid 1000 appuser \
    && mkdir /app \
    && chown appuser:appuser /app
WORKDIR /app

# Сначала только requirements.txt: слой с зависимостями кэшируется
# и пересобирается, только когда меняется этот файл
COPY requirements.txt .
RUN pip install -r requirements.txt

# ---------- dev-этап: код и запуск с автоперезагрузкой ----------
FROM base AS dev

# Код копируется в образ (нужен для тестов и первого запуска);
# при разработке изменения подтягивает Docker Compose Watch
COPY --chown=appuser:appuser . .

USER appuser
EXPOSE 8000

# --reload перезапускает сервер при изменении файлов в app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "app"]
