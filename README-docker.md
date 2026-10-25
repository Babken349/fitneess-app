# Запуск backend и PostgreSQL в Docker (для разработки)

Нужен только **Docker Desktop** (Compose версии 2.22 или новее). Python и PostgreSQL ставить не надо.

## Файлы и правки в коде

Положите в корень backend-репозитория (рядом с `app/`, `alembic/`, `requirements.txt`):

- `Dockerfile`, `docker-compose.yml`, `.env.example`, `.dockerignore`
- `docker/postgres/init-test-db.sh`

В файл `.gitattributes` добавьте, чтобы shell-скрипты и Dockerfile не получали переводы строк Windows (иначе ошибка `exec format error`):

```
*.sh text eol=lf
Dockerfile text eol=lf
docker-compose.yml text eol=lf
```

В `.gitignore` убедитесь, что есть: `.env`, `.env.test`, `venv/`, `htmlcov/`, `.coverage`, `all_models_output.txt`.

**Две правки в коде (CORS из настроек).**

`app/core/config.py`, внутри класса `Settings` добавить:

```python
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
```

`app/main.py`, заменить блок `add_middleware`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,  # токены идут в заголовке Authorization, куки не используются
    allow_methods=["*"],
    allow_headers=["*"],
)
```

В `requirements.txt` удалите первую строку, если там попала строка вроде `app.main:app ...`, и пакет `run==0.3`, если он не используется.

## Первый запуск

```bash
cp .env.example .env
# в .env замените SECRET_KEY: openssl rand -hex 32
# при желании поменяйте пароль базы (в трёх местах: POSTGRES_PASSWORD, DATABASE_URL, TEST_DATABASE_URL)
docker compose up --build --watch
```

При старте backend сам применяет миграции (`alembic upgrade head`). Первая сборка занимает несколько минут.

## Адреса

| Что | Адрес |
|---|---|
| Swagger | http://localhost:8000/docs |
| API | http://localhost:8000/api/v1 |
| OpenAPI-файл | http://localhost:8000/openapi.json |
| PostgreSQL с хоста | `localhost:5433` (логин и пароль из `.env`) |
| Frontend через nginx (необязательно) | http://localhost:8080 |

Фронтенд в `config.js` обращается к `http://localhost:8000`, а не к `http://db:5432`: имя `db` понимают только контейнеры.

## Команды

```bash
docker compose up --watch                 # обычный запуск с автоперезагрузкой
docker compose up -d                      # запуск в фоне (без отслеживания файлов)
docker compose --profile web up --watch   # то же и фронтенд через nginx
docker compose down                       # остановка (данные базы сохраняются)
docker compose down -v                    # полный сброс, база будет создана заново
docker compose logs -f backend            # логи backend (аналогично db, frontend)
docker compose exec backend sh            # войти в контейнер backend
docker compose exec db psql -U fitness -d fitness   # консоль PostgreSQL
docker compose run --rm backend pytest -q # тесты в контейнере
docker compose up -d --force-recreate backend   # после правки .env
```

## Как это работает

- **Dockerfile** описывает образ одного сервиса (Python, зависимости, код). **docker-compose.yml** описывает, какие сервисы запускать вместе, как их соединить, какие порты и тома использовать.
- **Том `pgdata`** хранит данные PostgreSQL вне контейнера. Без него база пропала бы при каждом пересоздании контейнера.
- **Адреса.** Backend и база общаются внутри сети Docker по имени сервиса: `db:5432`. Браузер находится снаружи, поэтому ходит на порт, проброшенный на хост: `localhost:8000`.
- **Автоперезагрузка.** `docker compose up --watch` копирует изменённые файлы из `app/`, `alembic/`, `tests/` в контейнер, `uvicorn --reload` видит их и перезапускает сервер. При изменении `requirements.txt` образ пересобирается сам. Это работает и тогда, когда репозиторий лежит на диске Windows (`/mnt/c/...`), где обычное отслеживание файлов в контейнере не срабатывает.
- **Тестовая база.** Скрипт `init-test-db.sh` создаёт базу `fitness_test` при первом запуске. Тесты отказываются работать на базе без суффикса `_test`.

## Частые ошибки

| Симптом | Решение |
|---|---|
| `port is already allocated` (8000 или 5433) | Остановите локальный uvicorn или поменяйте `BACKEND_PORT` и `DB_PORT` в `.env` |
| `exec format error` или `\r: command not found` | Файл с переводами строк Windows: добавьте правила в `.gitattributes` и пересоздайте файл с LF |
| Backend падает с `ValidationError ... Field required` | В `.env` не хватает переменной из `.env.example` (проверьте `SECRET_KEY`, `RESEND_API_KEY`, `EMAIL_FROM`, `FRONTEND_URL`) |
| Меняю `POSTGRES_PASSWORD`, а в базе старый | Пароль применяется только при первом создании тома: `docker compose down -v` и запуск заново |
| `database "fitness_test" does not exist` | Том уже существовал до скрипта: `docker compose exec db createdb -U fitness fitness_test` |
| В браузере CORS error | Адрес страницы фронтенда должен быть в `CORS_ORIGINS` (без слеша в конце, с портом), затем `docker compose up -d --force-recreate backend` |
| Изменения кода не подхватываются | Запускайте с флагом `--watch` |
| Письма не приходят | В dev используется заглушка ключа Resend, письма не отправляются |

## Чек-лист проверки

```bash
docker compose config                       # конфигурация читается без ошибок
docker compose ps                           # db: healthy, backend: healthy
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/docs     # 200
docker compose exec backend alembic current # показывает последнюю ревизию
docker compose exec db psql -U fitness -d fitness -c "\dt"              # таблицы созданы
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier":"nobody","password":"x"}'                           # 401 Unauthorized
curl -s -i -X OPTIONS http://localhost:8000/api/v1/auth/login \
  -H "Origin: http://localhost:5500" \
  -H "Access-Control-Request-Method: POST" | grep -i access-control     # есть Allow-Origin
docker compose run --rm backend pytest -q   # тесты проходят на базе fitness_test
```

Последняя проверка связывает все сервисы: фронтенд с backend через CORS, backend с базой через миграции и тесты.

## Демо-данные (seed)

```bash
docker compose exec backend python -m app.seed
```

Скрипт можно запускать повторно: существующее не дублируется. Создаёт справочник упражнений, программу «Базовая» (три тренировки) и данные за 14 дней для `demo_athlete`.

| Логин | Email | Роль |
|---|---|---|
| demo_athlete | athlete@example.com | участник с данными за 14 дней и программой |
| demo_empty | empty@example.com | участник без данных |
| demo_researcher | researcher@example.com | исследователь |
| demo_admin | admin@example.com | администратор |
| demo_unverified | unverified@example.com | email не подтверждён |

Пароль для всех: `DemoPass123!` (можно задать своим через `SEED_PASSWORD`). Вход по логину или email. Только для локальной разработки.
