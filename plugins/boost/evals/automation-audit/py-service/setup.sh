#!/usr/bin/env bash
# Python-сервис с уже настроенными хуком ruff и Context7; .env с фейковыми значениями.
set -euo pipefail
cp -r "$(dirname "$0")/../_fixture/py-service/." .
cp .env.example .env
