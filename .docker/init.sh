#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    SELECT 'CREATE DATABASE ${POSTGRES_DB}'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${POSTGRES_DB}');\\gexec
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    SELECT 'CREATE DATABASE ${POSTGRES_DB}_test'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${POSTGRES_DB}_test');\\gexec
EOSQL
