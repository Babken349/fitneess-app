#!/bin/sh
# Выполняется один раз при первом создании тома: создаёт тестовую базу <POSTGRES_DB>_test.
# Если том уже существует, создайте базу вручную:
#   docker compose exec db createdb -U "$POSTGRES_USER" fitness_test
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE "${POSTGRES_DB}_test";
EOSQL
