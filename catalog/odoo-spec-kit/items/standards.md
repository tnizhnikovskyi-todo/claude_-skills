# Стандарты `docs/*` и `CLAUDE.md` (odoo-spec-kit)

- **Тип:** правила для агента (`CLAUDE.md`/`AGENTS.md` → `docs/base-standards.md`, 4 документа `alwaysApply: true`)
- **Источник:** `focuz-ai/odoo-spec-kit@23df08b` (ветка `19.0`, дерево = `16.0`), `docs/`
- **Дата разбора:** 2026-11-03
- **Вердикт:** отклонить

## Что делает

Задаёт агенту принципы (SDD, «Anti-Vibe-Coding», маленькие шаги, типы), правила языка (документы по-испански, код
и UI-строки по-английски, перевод через `.po`, `es_419` по умолчанию), backend/frontend-стандарты с примерами, словарь
«неубиваемых» моделей (`res.partner`, `product.template/product`, `account.move`, `hr.contract`…) и совет читать живую
схему через `mcp-server-odoo` (`odoo://{model}/fields`) перед предложением полей.

## Сверка с `odoo@19.0` (`e0b25b7`)

Полная таблица в `../notes.md`. Неверно или устарело для 19.0: `attrs`/`states` как обязательные
(`ir_ui_view.py:495-497`), `<tree>` (`ir_ui_view.py:149`), `type='json'` (`http.py:812-818`), XML-RPC/JSON-RPC как
основной путь интеграции (`addons/rpc/controllers/__init__.py:6-11`), `read_group` (`orm/models.py:2754`),
`_sql_constraints` (`orm/model_classes.py:162-164`), `hr.contract` (в community 19.0 — `hr.version`),
`SavepointCase`, `div.oe_chatter`, PostgreSQL 12+ (`release.py:41` — 13), `useService("rpc"/"user")`, регистрация
виджета классом (`views/fields/field.js:65-75`), QUnit-хелперы `tests/helpers/` (в 19.0 Hoot). Совет «вместо
`sudo()` — `with_user(SUPERUSER_ID)`» ложный: это тоже суперрежим (`orm/models.py:5999-6007`).

Верно: `@api.model_create_multi`, `Command`, `check_company`, `precompute`, параметризация SQL, `t-raw` устарел,
запрет `cr.commit()`.

## Сравнение с нашим

- `templates/CLAUDE.md` — ~45 строк поведения без фактов версии; факты — в `source-check` и T1 с `файл:строка`.
  Их подход «факты прямо в постоянном контексте» дорог (~700 строк) и опасен: одна устаревшая версия ломает всё.
- Словарь моделей — то же, что наш T1, но без источников и с ошибкой (`hr.contract`).
- «Живая схема через MCP перед новыми полями» — у нас есть `odoo-connector` (`odoo_get_fields`); правило уже по
  смыслу в `tr-odoo-tech-design` («звіряє з документацією»), но про живую базу клиента — не видели; мелкая идея,
  в «Что взять» не включена (нужен текст скилла).

## Оценка

Прирост 0, надёжность 0 (на 19.0 вредит). Брать нечего, кроме урока: версия в шапке без барьера не работает.
