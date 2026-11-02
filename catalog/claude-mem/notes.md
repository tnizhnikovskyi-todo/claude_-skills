# claude-mem: рабочий журнал

## 2026-11-02

- Склонирован https://github.com/thedotmack/claude-mem в scratchpad
  (вне репозитория). HEAD `26ccf4d`, 2026-11-02, версия 15.8.3, Apache-2.0.
  Код только читаем, ничего не запускаем.
- Активность: 3834 коммита всего, ~1460 с августа 2026; релизы v15.x.
- Структура: `plugin/` (плагин Claude Code: hooks.json, .mcp.json, skills,
  scripts/*.cjs бандлы), `src/` (исходники TS), `cowork/` (отдельный
  плагин для облачных сессий, шлёт tool use на cmem.ai), интеграции для
  Codex, Cursor, OpenCode, Grok и др.
- Первое, что бросилось в глаза: README говорит, что установщик по умолчанию
  предлагает войти в аккаунт claude-mem и использовать «claude-mem observer»
  (хостинговый, 30 дней триала) — то есть по умолчанию сжатие может идти
  через их облако, а не через Anthropic.

### Что проверено по коду (только чтение)

| Вопрос | Ответ | Где |
|---|---|---|
| Какие хуки | Setup, SessionStart×3, UserPromptSubmit, PreToolUse (Read/Bash/Grep/Glob), PostToolUse + PostToolUseFailure (`*`), Stop, SubagentStop, SessionEnd | `plugin/hooks/hooks.json` |
| Что пишется | Полный `tool_input`/`tool_response`, промпты, последнее сообщение ассистента, deliverables | `src/cli/handlers/observation.ts`, `session-init.ts`, `summarize.ts` |
| Пропуск инструментов | `CLAUDE_MEM_SKIP_TOOLS`, `CLAUDE_MEM_SKIP_BASH_PATTERNS` (regex), `CLAUDE_MEM_EXCLUDED_PROJECTS` (glob) | `SettingsDefaultsManager.ts` |
| Маскировка секретов | Есть, 21 + 4 generic шаблона, **по умолчанию выкл.** | `docs/public/usage/auto-redaction.mdx` |
| `<private>` | Вырезается из промптов/полей до хранения | `src/sdk/prompts.ts`, `prompt-storage.ts` |
| Наблюдатель | Agent SDK, `haiku`, auth `subscription`, `tools: []` и прочая изоляция | `ClaudeProvider.ts`, `src/sdk/hardened-options.ts` |
| Обрезка полей для наблюдателя | 16 000 символов (голова + хвост) | `src/sdk/prompts.ts:170` |
| Порт | `127.0.0.1`, `37700 + uid%100`; без токена для запросов без Origin | `SettingsDefaultsManager.ts`, `worker/http/middleware.ts` |
| Телеметрия | PostHog, opt-out (по умолчанию ВКЛ), белый список полей | `services/telemetry/consent.ts`, `docs/public/telemetry.mdx` |
| Облако | `sync.cmem.ai` выкл. по умолчанию; установщик в интерактиве предлагает вход и триал Pro | `README.md`, defaults |
| Установка | `curl -fsSL https://bun.sh/install \| bash`, `curl … astral.sh/uv/install.sh \| sh` через `execSync` | `src/npx-cli/install/setup-runtime.ts:144,182` |
| Инжект на старте | ≤ 10 000 символов | `src/services/context/ContextBudget.ts:9` |
| File Read Gate | deny целого `Read` файла ≥ 32 КБ с историей (кроме md/yaml/toml) | `src/cli/handlers/file-context.ts` |
| MCP-инструменты | ~26 (README говорит «4») | `src/servers/mcp-server.ts` |
| Удаление | `uninstall` сохраняет `~/.claude-mem` | `src/npx-cli/commands/uninstall.ts:484` |
| Активность | 3834 коммита с 2025-09; 878 за октябрь 2026; основной автор Alex Newman (1057 с мая) | `git log` |

Звёзды/issues через API GitHub получить не удалось (запрос из контейнера
без данных), не критично.

### Решения

- Ядро: адаптировать, 11/18. Cowork: отклонить (безопасность 0).
- Ничего не запускали; испытания нет. Если пользователь разрешит — прогнать
  в одноразовом контейнере на игрушечном проекте и замерить реальный объём
  инжекта и расход токенов наблюдателя.

### Открытые вопросы

- Поддерживает ли `CLAUDE_MEM_SKIP_TOOLS` шаблоны вида `mcp__*` (проверить
  `src/shared/is-tool-skipped.ts`).
- Точный формат glob в `CLAUDE_MEM_EXCLUDED_PROJECTS`.
- Реальный расход токенов наблюдателя на типичную сессию.
- Что именно делает `Setup`-хук `version-check.js` (минифицирован в `plugin/scripts`).
