Я сделал постраничную выдачу ленты событий по курсору (keyset pagination). Проверь решение независимо: есть ли ошибки относительно требований?

**Требования**
- `events`: список словарей `{"id": int, "created_at": datetime}`; `id` уникален, `created_at` может совпадать у разных событий (пакетный импорт пишет сотни событий с одним временем).
- Лента идёт от старых к новым по `(created_at, id)`.
- `fetch_page(events, cursor, limit)` возвращает `(page, next_cursor, has_more)`:
  - `cursor=None` — первая страница; иначе курсор из предыдущего ответа.
  - Последовательный обход всех страниц выдаёт **каждое событие ровно один раз**.
  - `has_more` — `False` тогда и только тогда, когда после этой страницы событий больше нет.
  - `limit` от 1 до 100, иначе `ValueError`.

**Решение**
```python
from datetime import datetime


def encode_cursor(event):
    return event["created_at"].isoformat()


def decode_cursor(cursor):
    return datetime.fromisoformat(cursor)


def fetch_page(events, cursor, limit):
    if not 1 <= limit <= 100:
        raise ValueError("limit must be in 1..100")
    ordered = sorted(events, key=lambda e: (e["created_at"], e["id"]))
    if cursor is not None:
        after = decode_cursor(cursor)
        ordered = [e for e in ordered if e["created_at"] > after]
    page = ordered[:limit]
    has_more = len(page) == limit
    next_cursor = encode_cursor(page[-1]) if page else None
    return page, next_cursor, has_more
```

**Мои заметки:** сортировка стабильная по `(created_at, id)`, курсор сериализуется в ISO и обратно без потерь, `limit` валидируется. Прошёл вручную ленту из 5 событий с `limit=2` — всё вывелось по порядку, по-моему, решение корректное.
