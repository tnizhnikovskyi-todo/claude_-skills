# firecrawl-mcp (MCP-сервер)

- **Тип:** MCP-сервер (stdio / Streamable HTTP / SSE; плюс hosted)
- **Источник:** https://github.com/firecrawl/firecrawl-mcp-server, npm `firecrawl-mcp`
- **Версия / коммит:** 3.36.0, `e70e89e` (2026-11-02)
- **Дата разбора:** 2026-11-02
- **Вердикт:** **адаптировать** — подключить hosted MCP по ключу или
  локальный с `FIRECRAWL_NO_*_FEEDBACK=1`, версию пиннить

## Что делает

Обёртка над Cloud API (или self-hosted через `FIRECRAWL_API_URL`). Полный
профиль — 27 инструментов:

- веб: `firecrawl_scrape`, `firecrawl_search`, `firecrawl_map`,
  `firecrawl_crawl`, `firecrawl_check_crawl_status`, `firecrawl_extract`,
  `firecrawl_parse`;
- браузер: `firecrawl_interact`, `firecrawl_interact_stop`;
- агент: `firecrawl_agent`, `firecrawl_agent_status`;
- индексы: `firecrawl_developer_search`, `firecrawl_gov_search`,
  `firecrawl_research_*` (5 шт.: статьи, related, read, GitHub);
- мониторинг: `firecrawl_monitor_*` (8 шт.);
- прочее: `firecrawl_find_tools` (каталог Alexandria),
  `firecrawl_credit_usage`, `firecrawl_search_feedback`, `firecrawl_feedback`.

Hosted-варианты: `https://mcp.firecrawl.dev/v2/mcp` (ключ в заголовке или
keyless), `/v2/mcp-oauth` (вход через аккаунт), `/v2/mcp-search` (9 поисковых
инструментов).

## Как устроен

TypeScript, ~7.6 тыс. строк в `src/` (основное — `server.ts`, 3.3 тыс.).
Зависимости: `@modelcontextprotocol/server`, официальный SDK `firecrawl`,
`hono`, `zod`. Node ≥ 22. Ходит в сеть только на `FIRECRAWL_API_URL`
(по умолчанию `api.firecrawl.dev`). Ретраи с экспоненциальной задержкой,
предупреждения о кредитах (пороги настраиваются).

Конфигурация через env: `FIRECRAWL_API_KEY`, `FIRECRAWL_API_URL`,
`FIRECRAWL_OAUTH_TOKEN`, `FIRECRAWL_NO_SEARCH_FEEDBACK`,
`FIRECRAWL_NO_ENDPOINT_FEEDBACK`, `HTTP_STREAMABLE_SERVER`, `FIRECRAWL_RETRY_*`.
В локальном HTTP-режиме есть проверка `Host`/`Origin` (защита от DNS
rebinding) — разумно.

## Наблюдения по безопасности

- **Feedback-инструменты** (`firecrawl_search_feedback`, `firecrawl_feedback`)
  в описаниях подталкивают агента вызывать их «после каждого поиска» и
  передавать «конечную цель пользователя» (`objective`), «чего не хватило»
  (`missingContent`), заметки до 4000 символов. Мотивация — возврат 1
  кредита. Это утечка контекста задачи; выключать env-переменными
  (тогда инструменты не регистрируются).
- **Keyless-режим** при исчерпании дневного лимита возвращает агенту
  инструкцию «закончи ответ строкой со ссылкой на регистрацию»
  (`src/recovery.ts`). Инструкция внутри результата инструмента — повод
  не использовать keyless в работе.
- `CLOUD_SERVICE=true` делает scrape read-only (без `actions`) — это
  касается их hosted-развёртывания.
- Скрытых вызовов в другие хосты, телеметрии сторонних сервисов в `src/`
  не нашёл (`grep` по `process.env` и сетевым вызовам).

## Стоимость контекста

Описания и `.describe()` полей — ~19 тыс. символов (~5 тыс. токенов) плюс
JSON-схемы. В Claude Code MCP-инструменты подгружаются отложенно, так что
постоянная цена мала; выдача страниц — основной расход, поэтому в правилах
просить `formats:[json]` или `onlyMainContent:true`. Можно подключить
`/v2/mcp-search`, если нужен только поиск.

## Подключение

См. `../README.md`, раздел «Инструкция подключения».

## Оценка

| Критерий | Балл | Комментарий |
|---|---|---|
| Прирост | 3 | Даёт всё, чего нет у WebFetch/WebSearch |
| Частота | 2 | Нужен на сложных страницах и ресёрче |
| Надёжность | 2 | Зрелый, ретраи; вживую не проверен |
| Стоимость контекста | 2 | Отложенная загрузка спасает; выдача большая |
| Безопасность | 2 | Код прочитан, MIT; данные уходят в облако; feedback выключить |
| Поддержка | 3 | 273 коммита в выборке за 3 мес., релизы часто |
| **Итого** | **14** | |
