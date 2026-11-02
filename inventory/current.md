# Что уже подключено

Снимок на 2026-11-02, облачная сессия Claude Code. Это база: новые кандидаты
сравниваем с тем, что тут уже есть.

## Встроенные скиллы Claude Code

| Скилл | Зачем |
|---|---|
| `code-review`, `simplify`, `security-review` | Ревью кода: баги, упрощение, безопасность |
| `claude-api` | Справка по Claude API и SDK |
| `workflow-authoring` | Оркестрация нескольких субагентов |
| `run` | Запуск приложения, чтобы увидеть изменение вживую |
| `loop` | Повторяющиеся задачи по интервалу |
| `update-config`, `fewer-permission-prompts`, `keybindings-help` | Настройка харнесса, хуки, права |
| `plugin-authoring` | Создание модов интерфейса и хуков |
| `session-start-hook` | Хуки старта сессии в репозитории |
| `init` | Генерация `CLAUDE.md` для проекта |
| `dataviz`, `artifact-design`, `artifact-diagramming`, `artifact-capabilities` | Визуализация и страницы-артефакты |

## Скиллы Anthropic (`anthropic-skills:*`)

`docx`, `pdf`, `pptx`, `xlsx`, `docs`, `skill-creator`, `google-workspace`,
`import-memory`, `morning`, а также рабочие скиллы команды
(`meeting-protocol-builder`, `tr-*`, `odoo-spec-writer`, `ite-konsultant` и др.).

## Плагины организации

| Плагин | Область |
|---|---|
| `odoo19-sales-prep`, `odoo19-sales-demo`, `odoo19-sales-offer` | Продажи: бриф, демо, КП, защита |
| `odoo19-discovery-initiation`, `-sessions`, `-closeout` | Дискавери |
| `odoo19-tr-authoring` | Технические требования |
| `odoo19-mvp-build` | Сборка MVP: спека, код, тесты, ревью |
| `odoo19-implementation` | Миграция, go-live, обучение, hypercare |
| `odoo-connector` | Живые данные Odoo |
| `ite-konsultant` | IT-Enterprise для Toyota |
| `enterprise-search` | Поиск по корпоративным источникам |
| `cowork-plugin-management` | Создание и настройка плагинов |

## MCP-коннекторы

Работают: GitHub, Gmail, Google Calendar / Docs / Drive / Sheets / Slides,
Fathom, AIKB, ITE-KB, Odoo, Unitalk, Claude Docs.

Требуют авторизации: OpenData_Bot, Atlassian, Guru, Notion, Slack
(через `enterprise-search`).

Не подключились: TripSyncTodoBot, Asana.

## Что бросается в глаза

- Много узкоспециализированных процессных скиллов (Odoo, продажи), мало
  общих «усилителей мышления»: исследование, проверка фактов, память.
- Нет отдельного MCP для актуальной документации библиотек.
- Нет постоянной памяти между сессиями, кроме `CLAUDE.md`.
