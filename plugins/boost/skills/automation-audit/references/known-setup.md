# Что уже есть: не советовать как новое

Снимок на 2026-11-02 (`inventory/current.md` и `plugins/boost/README.md`
репозитория claude_-skills). Если в сессии видно больше или меньше —
верь сессии.

## Плагин `boost` (этот плагин)

| Скилл / хук | Что делает | Дубль, если советуешь… |
|---|---|---|
| `interview-me` | Уточнение задачи по одному вопросу, работа после «да» | скилл/правило «сначала задавай вопросы» |
| `source-check` | Версия → официальный источник → цитата с URL, иначе `UNVERIFIED` | скилл «проверяй API Odoo по докам» (но Context7 — не дубль: это данные) |
| `cloud-memory` + хуки `SessionStart`/`Stop` | Память проекта в `memory/` в git, подмешивание на старте | Memory MCP, свой хук памяти, «веди заметки между сессиями» |
| `lean-change` | Минимальное полное изменение, без срезания проверок | скилл/правило «не переусложняй» |
| `repo-audit` | Аудит кода: долги, мёртвый код, безопасность, ранжированный отчёт | субагент `code-reviewer`/`architect` для аудита |
| `odoo-model-map` | Карта `_inherit`, вью, прав и `ir.rule` по строкам и XML | скилл/субагент «найди, кто расширяет модель», graph/LSP-MCP для Odoo |
| `automation-audit` | Этот скилл | |

Хуки `boost` молчат без `memory/`. Значит, если `memory/` нет, правильная
рекомендация: «создать `memory/INDEX.md`, чтобы включить уже установленный
`cloud-memory`», а не новый механизм памяти.

## Встроенные скиллы Claude Code

`code-review`, `simplify`, `security-review` (ревью диффа/PR), `init`
(пишет `CLAUDE.md`), `update-config` (хуки и права в `settings.json`),
`fewer-permission-prompts` (allowlist по транскриптам), `session-start-hook`
(SessionStart-хук в репозитории), `run` (запуск приложения), `loop`,
`plugin-authoring`, `workflow-authoring`, `claude-api`, `dataviz`,
артефакты. Дубль: субагенты `code-reviewer`, `security-reviewer`,
скилл «напиши CLAUDE.md», «настрой хук» как отдельный скилл.

## Скиллы и плагины организации

- `anthropic-skills:*`: `docx`, `pdf`, `pptx`, `xlsx`, `docs`,
  `skill-creator`, `google-workspace`, `security-review` (Odoo `td.*` перед
  деплоем), `odoo-spec-writer`, `tr-*`, протоколы встреч. Дубль: «поставить
  docx/pdf/xlsx-скиллы», «скилл для ТР».
- Плагины: `odoo19-mvp-build` (спека, код, тесты, ревью), `odoo19-tr-authoring`,
  `odoo19-implementation`, дискавери и продажи `odoo19-*`, `odoo-connector`
  (живые данные Odoo), `enterprise-search`, `cowork-plugin-management`.
  Дубль: «скилл генерации модуля/тестов Odoo», второй Odoo-MCP.

## MCP-коннекторы claude.ai

Подключены: GitHub, Gmail, Google Calendar/Docs/Drive/Sheets/Slides,
Fathom, AIKB, ITE-KB, Odoo, Unitalk, Claude Docs. Дубль: GitHub MCP в
`.mcp.json`, Google-MCP.
Требуют авторизации (рекомендация = «авторизовать», а не «поставить»):
Atlassian, Notion, Slack, Guru.

**Нет:** MCP актуальной документации библиотек → Context7 (не дубль).

## Готовые шаблоны (репозиторий claude_-skills, `templates/`)

| Файл | Куда | Признаки, что уже применён |
|---|---|---|
| `templates/CLAUDE.md` (~40 строк) | корень репо как `CLAUDE.md` или дописать | «Пол качества», `shortcut: <предел>, <когда апгрейдить>`, «Не проверено / риск», «Отсутствие не доказывается поиском», `UNVERIFIED` |
| `templates/mcp.json` | корень репо как `.mcp.json` | `.mcp.json` с `context7`, `https://mcp.context7.com/mcp`, `${CONTEXT7_API_KEY}` |

Раздел «Context7» шаблона `CLAUDE.md` убирают, если сервер не подключён:
его отсутствие при остальных разделах — это «шаблон применён, Context7 ещё
нет», а не «шаблон не применён». Инструкция подключения: `templates/README.md`
(ключ в секреты окружения, домены в allowlist, новая сессия, проверка `/mcp`).
