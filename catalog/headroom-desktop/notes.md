# Рабочий журнал: headroom-desktop

## 2026-11-02 — первичный разбор

**Что сделали**

- Склонировали `gglucass/headroom-desktop` в scratchpad (вне репозитория).
  Коммит `4390af7b` от 2026-10-31. Ничего не запускали.
- Прочитали `README.md`, `LICENSE` (MIT, Garm Tech BV), `docs/architecture.md`,
  `research/tool-compatibility-matrix.md`, `.claude/settings.json`.
- Прошлись grep'ом по `src-tauri/src` (~126 тыс. строк Rust): внешние URL,
  работа с токенами, payload'ы на бэкенд, Sentry, хуки.

**Активность:** первый коммит 2026-03-30, ~2160 коммитов, 688 за октябрь 2026;
основной автор Garm (Garm Lucassen); есть Dependabot, CI с проверкой релиза.

**Ключевые находки по безопасности** (`src-tauri/src/`)

- `bearer.rs`, `state.rs:2210`: OAuth-токен Claude захватывается из
  проходящих через прокси запросов, хранится в памяти до 1 ч.
- `pricing.rs:2436`, `pricing.rs:3451`: с этим токеном приложение само ходит
  в `api.anthropic.com/api/oauth/usage` и `/api/oauth/profile`.
- `pricing.rs:3227`: читает `~/.claude.json` (`oauthAccount`);
  `pricing.rs:3112`: читает `~/.codex/auth.json`.
- `pricing.rs:2091`, `:2191`, `:4366`: бэкенд `extraheadroom.com/api/v1` —
  `desktop/milestones` (токены сэкономлено + снимок экономии, если включён
  шаринг), `desktop/weekly_limit`, `desktop/config`. Отправки самого
  OAuth-токена на свой бэкенд не нашли.
- `pricing.rs:3756`: в Sentry уходят поля организации Anthropic при
  неизвестном тарифе.
- `proxy_intercept.rs:3617`: тело ошибок провайдера остаётся в локальном
  логе, в Sentry только структурная сводка.
- `analytics.rs`: Aptabase, белый список событий, выключается
  (`sharing_enabled`).
- `client_adapters.rs:3880`, `:11297`: PreToolUse-хук `rtk` на Bash;
  выдаёт `allow` для переписанных read-only команд в режимах
  default/acceptEdits/dontAsk/bypassPermissions.
- `lib.rs:5960`: `headroom learn` пишет в `CLAUDE.local.md` (раньше в
  `CLAUDE.md`) и в память проекта; `memory_scrubber.rs` чистит вредные
  «выученные» правила от старых версий.
- `tool_manager.rs:37`, `:2680`: компоненты закреплены по версии и SHA-256.

**Вывод по облаку:** приложение только для локальной машины. В облачной
сессии нет трея, пользовательского `~/.claude`, а API-трафик идёт через
управляемый прокси среды. Не применимо.

## Открытые вопросы

- Разобрать `rtk` отдельно: реальная экономия на наших командах, безопасность
  кода, можно ли поставить хук без авто-`allow`.
- Разобрать `context7` отдельно (закрывает пробел «нет MCP для документации»).
- Код `headroom-ai` (headroomlabs-ai/headroom) не читали.
- Нужно ли кому-то в команде локально (Claude Code на ноутбуке с подпиской)?
  Если да — согласование с ИБ из-за MITM и перехвата токена.
