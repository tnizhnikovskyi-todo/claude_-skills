# claude-mem (ядро, `plugin/`)

- **Тип:** плагин Claude Code: хуки + MCP-сервер + скиллы + фоновый воркер
- **Источник:** https://github.com/thedotmack/claude-mem/tree/main/plugin
- **Версия / коммит:** 15.8.3, `26ccf4d`
- **Дата разбора:** 2026-11-02
- **Вердикт:** адаптировать (как есть не ставить)

## Что делает

Автоматически записывает работу в сессии и сжимает её моделью-наблюдателем
в «наблюдения» и сводки. На старте следующей сессии подмешивает их индекс
и даёт MCP-поиск по истории.

## Какую слабость Claude закрывает

Нет памяти между сессиями. Claude заново изучает проект, повторяет
отброшенные решения и наступает на уже исправленные баги.

## Как устроен

### Поток данных

```
хук PostToolUse (каждый инструмент)
  → claude-mem hook claude-code observation
  → spool / HTTP на воркер 127.0.0.1:377xx
  → SQLite (~/.claude-mem) + очередь
  → наблюдатель: Claude Agent SDK, модель haiku, tools: [] (без инструментов)
  → наблюдения (decision/bugfix/feature/refactor/discovery/change) + эмбеддинги в Chroma
хук Stop → сводка сессии (берёт последнее сообщение ассистента)
хук SessionStart → индекс наблюдений в контекст (≤ 10 000 символов)
хук PreToolUse(Read|Bash|Grep|Glob) → таймлайн наблюдений по файлу; может запретить Read
MCP mcp-search → search / timeline / get_observations / smart_* / corpus / work_state …
```

### Хуки (`plugin/hooks/hooks.json`)

| Событие | Команда | Синхронный? | Что делает |
|---|---|---|---|
| `Setup` | `node version-check.js` через длинный `/bin/sh -c` | да | Ищет установленную версию плагина, проверяет зависимости |
| `SessionStart` | `claude-mem start` | async | Поднимает воркер (Bun) |
| `SessionStart` | `claude-mem hook claude-code context` | да | Инжект контекста (индекс наблюдений, work-state, инструкции по памяти) |
| `SessionStart` (startup) | `node ensure-launcher.cjs` | да, до 180 с | Ставит/обновляет бинарник `claude-mem` в PATH |
| `UserPromptSubmit` | `… session-init` | да, 15 с | Регистрирует ход и **текст промпта** |
| `PreToolUse` `Read\|Bash\|Grep\|Glob\|memory*` | `… file-context` | да, 15 с | Таймлайн по файлу; File Read Gate: `permissionDecision: deny` для целого чтения файла ≥ 32 КБ с историей |
| `PostToolUse`, `PostToolUseFailure` `*` | `… observation` | async | Полный `tool_input` + `tool_response` в воркер |
| `Stop` | `… summarize` | async | Сводка хода, копия deliverables |
| `SubagentStop`, `SessionEnd` | … | async | Закрытие |

Источник: `src/cli/handlers/*.ts`. Хендлеры «fail-open»: при ошибке воркера
не ломают сессию.

### Что сохраняется

- `src/cli/handlers/observation.ts`: `toolInput` и `toolResponse` целиком
  (с ограничением размера JSON), `cwd`, id агента. Пропускаются только
  инструменты из `CLAUDE_MEM_SKIP_TOOLS` (по умолчанию
  `ListMcpResourcesTool,SlashCommand,Skill,TodoWrite,AskUserQuestion`) и
  сами инструменты памяти. **Вывод MCP-коннекторов (Gmail, Odoo, Drive,
  Unitalk) пишется так же, как вывод Bash.**
- Промпты пользователя (без частей в `<private>`).
- Последнее сообщение ассистента для сводки.
- `CLAUDE_MEM_DELIVERABLES_ENABLED=true`: копии файлов-результатов хода в
  `~/.claude-mem/deliverables/<project>/`.
- `CLAUDE_MEM_TRANSCRIPTS_ENABLED=true`: вотчер транскриптов (для Codex
  `~/.codex/sessions`).
- Скриншоты: по умолчанию выкл.

### Что уходит наружу

| Куда | Когда | Что |
|---|---|---|
| Модель-наблюдатель | всегда | Каждое событие инструмента (поля обрезаются до 16 000 символов с головой и хвостом) + промпты. По умолчанию `CLAUDE_MEM_PROVIDER=claude`, `CLAUDE_MEM_MODEL=haiku`, аутентификация `subscription` (логин Claude Code) |
| Резервный провайдер | при исчерпании квоты | `CLAUDE_MEM_QUOTA_FALLBACK_PROVIDER=claude` по умолчанию; можно `gemini`/`openrouter`, тогда данные идут третьей стороне |
| PostHog (`us.i.posthog.com`) | по умолчанию ВКЛ | Обезличенные метрики по белому списку полей (версия, ОС, длительности, счётчики). Содержимого нет. Выкл: `DO_NOT_TRACK=1` или `npx claude-mem telemetry disable` |
| `sync.cmem.ai` | только если задан `CLAUDE_MEM_CLOUD_SYNC_HUB_URL` | Наблюдения, сводки и (если вкл.) медиа |
| cmem.ai Pro-наблюдатель | если выбрать при установке (предлагается по умолчанию в интерактиве) | Сырые события |
| bun.sh, astral.sh, PyPI, HF | установка / первый старт Chroma | `curl \| bash`, `uvx chroma-mcp`, модель `all-MiniLM-L6-v2` |

### Сеть и процессы

- Воркер: Bun, HTTP на `127.0.0.1`, порт `37700 + uid % 100`
  (`SettingsDefaultsManager.ts`). Браузерные запросы проверяются по `Origin`
  (DELETE только со своей страницы). Запросы **без** `Origin` (хуки, curl,
  любой локальный процесс) доверены по модели «loopback-trust» без токена
  (`src/services/worker/http/middleware.ts`). Любой процесс пользователя
  может читать всю память по HTTP. Воркер не завершается по простою
  (`CLAUDE_MEM_IDLE_EXIT_SEC=0`).
- Chroma: процесс `chroma-mcp` через `uvx`.
- Наблюдатель: отдельный процесс `claude` (Agent SDK). Защищён хорошо:
  `tools: []`, `allowedTools: []`, `disallowedTools`, `permissionMode:
  dontAsk`, `canUseTool` → deny с аудитом, `mcpServers: {}`,
  `settingSources: []`, cwd-jail (`src/sdk/hardened-options.ts`).
  Prompt-injection из вывода инструмента не даст наблюдателю выполнить
  действие, но может исказить сохранённое наблюдение, которое потом попадёт
  в контекст главной сессии.

### Стоимость контекста

- `SessionStart`: до `CONTEXT_OUTPUT_LIMIT = 10 000` символов
  (`ContextBudget.ts`), по умолчанию 50 наблюдений и 10 сессий.
- Описания 30 скиллов плагина: ~7,9 КБ.
- MCP-сервер: ~26 инструментов (в Claude Code они обычно отложены через
  ToolSearch, но названия всё равно видны).
- `PreToolUse` на каждый `Read`/`Grep`/`Bash`: таймлайн до 15 строк по файлу.
- `CLAUDE_MEM_SEMANTIC_INJECT` (подмешивание на каждый промпт) по умолчанию
  выкл.

### Удаление

`npx claude-mem uninstall` удаляет плагин, кэш и лаунчер, но **сохраняет**
`~/.claude-mem` (БД, логи, deliverables, `.env` с ключами). Полная очистка:
`rm -rf ~/.claude-mem`. Удаление отдельных наблюдений: через viewer на
`http://127.0.0.1:<порт>/viewer` или API. При включённой синхронизации
удаления уходят «надгробиями» в облако.

## Проверка

Не запускали: по правилам репозитория чужой код без разрешения пользователя
не исполняем. Для испытания нужен отдельный контейнер или ВМ, данные
некоммерческого проекта и разрешение пользователя.

| Задача | Без него | С ним |
|---|---|---|
| Продолжить вчерашнюю задачу в новой сессии | — | — (не испытано) |

## Оценка

| Критерий | Балл | Комментарий |
|---|---|---|
| Прирост | 2 | Закрывает пробел памяти, но эффект не измерен; частично заменяется дисциплиной `CLAUDE.md`/handoff |
| Частота | 3 | Каждая сессия |
| Надёжность | 1 | Bun + uv + Chroma + воркер + лаунчер в PATH; огромная скорость изменений; гейт `Read` меняет поведение Claude |
| Стоимость контекста | 1 | ~5 тыс. токенов постоянно + добавки на чтение файлов; плюс токены наблюдателя на подписке |
| Безопасность | 1 | Открытый код и хорошая изоляция наблюдателя, но захват всего вывода по умолчанию, маскировка opt-in, телеметрия opt-out, localhost API без токена, `curl \| bash` |
| Поддержка | 3 | Очень активен, Apache-2.0 |
| **Итого** | **11/18** | |

## Риски и заметки

- Главный риск для нас: клиентские данные из MCP-коннекторов и секреты из
  вывода `Bash` оседают в SQLite и проходят через наблюдателя. `<private>`
  работает только для текста, который пользователь сам набрал в промпте.
- Скиллы плагина конкурируют с нашими (см. `bundled-skills.md`).
- Коммерческая воронка: триал cmem.ai Pro, TeamBrain, cloud-sync.
