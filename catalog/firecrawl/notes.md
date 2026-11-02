# Рабочий журнал: firecrawl

## 2026-11-02 — первичный разбор

### Что смотрели

Склонировано в scratchpad (вне репозитория), ничего не запускалось:

- `firecrawl/firecrawl` @ `6b02a6c` (2026-11-02, тег v2.11.645): README,
  `SELF_HOST.md`, `docker-compose.yaml`, `apps/api/src/search/index.ts`
  (порядок поиска: Fire-engine → SearXNG → DuckDuckGo), лицензии
  (корень AGPL-3.0, SDK MIT), `skills/` (build-скиллы).
- `firecrawl/firecrawl-mcp-server` @ `e70e89e` (3.36.0): README,
  `src/server.ts` (список инструментов, feedback-инструменты),
  `src/index.ts` (keyless-режим, env-флаги отключения feedback),
  `src/recovery.ts` (текст для агента при исчерпании keyless-лимита),
  все обращения к `process.env`.
- `firecrawl/cli` @ `a9a46fe` (1.26.24): README, 13 `SKILL.md`,
  `rules/security.md`, `rules/install.md`, `src/utils/web-defaults.ts`
  (deny `WebSearch`/`WebFetch` для Claude Code), `src/commands/setup.ts`.
- Цены: firecrawl.dev/pricing (через WebFetch, 2026-11-02).

### Что проверили / выяснили

- Активность: в выборке последних 200 коммитов монорепо все — за октябрь
  2026; 273 коммита MCP с августа. Основные авторы — сотрудники компании.
- Описания инструментов MCP: ~19 тыс. символов (скрипт по шаблонным
  строкам `description:` и `.describe(`), без JSON-схем.
- Feedback-инструменты собирают цели пользователя и «чего не хватило»;
  отключаются `FIRECRAWL_NO_SEARCH_FEEDBACK=1`,
  `FIRECRAWL_NO_ENDPOINT_FEEDBACK=1`.
- Keyless-лимит: в выводе инструмента инструкция агенту добавить в ответ
  ссылку на регистрацию.
- `firecrawl setup defaults` пишет `WebSearch`, `WebFetch` в
  `permissions.deny` Claude Code.
- Self-host без Fire-engine: Playwright + fetch, поиск DDG/SearXNG,
  LLM-функции требуют своего OpenAI/Ollama.
- ZDR — только Enterprise; DPA — с Standard.

### Чего не делали

- Живой прогон: нет ключа, keyless-запросы = отправка данных в их облако,
  нужно согласие пользователя.
- Не проверяли, какие облачные фичи (agent, индексы) реально работают в
  self-host.
- Не читали политику хранения данных (privacy policy / DPA) целиком.

### Открытые вопросы к пользователю

1. Есть ли ключ / готовы ли завести Free-аккаунт для живого сравнения с
   WebFetch/WebSearch на наших задачах?
2. Какие веб-задачи у команды типичны (ресёрч конкурентов, документация
   Odoo, сбор данных с сайтов клиентов)? От этого зависит «Частота».
3. Допустимо ли, что URL и контент уходят в облако Firecrawl (США)?
