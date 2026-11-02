# claude-automation-recommender (единственный скилл плагина)

- **Тип:** скилл
- **Источник:** `plugins/claude-code-setup/skills/claude-automation-recommender/`
  в `anthropics/claude-plugins-official` @ `a7ba5b9`
- **Дата разбора:** 2026-11-02
- **Вердикт:** адаптировать. Таблица признаков и справка по frontmatter
  стоят того, чтобы их взять; сам скилл ставить незачем.

## Как устроен SKILL.md

Три фазы:

1. **Анализ репо.** `ls`/`cat` манифестов, `.claude/`, `CLAUDE.md`, папок
   `src/ app/ tests/ ...` и таблица признаков: язык, фронтенд, бэкенд, БД,
   внешние API, тесты, CI, трекер, документация.
2. **Рекомендации** по таблицам «признак → что ставить»:
   - MCP: context7, Playwright, Supabase, Convex, Postgres, GitHub, Linear,
     AWS, Slack, Memory, Sentry, Docker;
   - скиллы: официальные (plugin-dev, commit-commands, frontend-design,
     hookify, feature-dev) и шаблоны своих (api-doc, create-migration,
     gen-test, pr-check, release-notes, project-conventions, setup-dev);
   - хуки: форматтер/линтер/type-check после Edit, тесты после Edit,
     запрет правки `.env` и lock-файлов;
   - субагенты: code-reviewer, security-reviewer, api-documenter,
     performance-analyzer, ui-reviewer, test-writer;
   - плагины: из официального маркетплейса.
3. **Отчёт** по шаблону: профиль кодовой базы, затем по 1–2 пункта на
   категорию с «Why» и «Where».

## Справочники (`references/`)

| Файл | Что полезного | Что не так |
|---|---|---|
| `mcp-servers.md` | Признаки для выбора MCP, совет коммитить `.mcp.json` | Команд установки почти нет; `--mcp-debug` под вопросом |
| `skills-reference.md` | Лучшая часть: frontmatter (`disable-model-invocation`, `user-invocable`, `allowed-tools`, `context: fork`, `agent`), `$ARGUMENTS`, подстановка `` !`cmd` ``, 8 шаблонов своих скиллов | Шаблоны под веб-разработку |
| `hooks-patterns.md` | Признак → хук для Prettier/ESLint/Ruff/Black/tsc/mypy/gofmt/rustfmt, защитные хуки, матчеры Notification | Готовых JSON для форматтеров нет; таблица повторяется дважды; уведомления только для macOS |
| `subagent-templates.md` | Шаблоны 8 субагентов с моделью и инструментами | Общие, без привязки к домену |
| `plugins-reference.md` | Список официальных плагинов, включая 11 LSP | Быстро устаревает |

## Что взять себе

1. Таблицу «признак в репо → автоматизация» как скелет для своего
   аудита, дописав Odoo: `__manifest__.py` → pylint-odoo/pre-commit,
   `odoo-connector` MCP, SessionStart-хук для облачных сессий.
2. Шаг «сначала прочитай `inventory/current.md`», чтобы не советовать
   уже установленное.
3. Справку по frontmatter — в наш `skill-creator`/`plugin-authoring` она
   частично уже входит, но шпаргалка компактная.
