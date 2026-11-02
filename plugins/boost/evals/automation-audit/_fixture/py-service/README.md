# billing-api

Сервис выставления счетов: FastAPI + PostgreSQL, платежи через Stripe.

## Разработка

```bash
uv sync
cp .env.example .env        # STRIPE_API_KEY, DATABASE_URL
uv run alembic upgrade head
uv run pytest
uv run ruff check . && uv run mypy billing
```

Миграции: `uv run alembic revision --autogenerate -m "..."`, файлы в
`migrations/versions/` руками не правим после мержа.
