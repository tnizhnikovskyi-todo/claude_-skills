# Признак в репозитории → автоматизация

Скелет таблиц взят из `claude-automation-recommender` (плагин
`claude-code-setup`, Anthropic, Apache 2.0; см. `attribution.md`),
переписан и дополнен Python/Odoo 19 и облачными сессиями. Рекомендуй
только при наличии признака; в отчёте «Подтверждено» = путь к признаку.

## Odoo 19 / Python

| Признак | Рекомендация | Категория | Цена / оговорка |
|---|---|---|---|
| `__manifest__.py` с `"version": "19.0.…"` | Context7 через `.mcp.json` (шаблон `templates/mcp.json`), libraryId `/websites/odoo/19.0`; после подключения — раздел «Context7» в `CLAUDE.md` | MCP | Ключ `CONTEXT7_API_KEY` в секреты окружения, домены `mcp.context7.com`, `context7.com` в allowlist; ~1000 бесплатных вызовов/мес. Главная слабость модели — поля, удалённые в 19.0 |
| `__manifest__.py`, нет доступа к Context7 | `source-check` из `boost` (уже есть) — цитата из доков 19.0 или `UNVERIFIED` | Скиллы | Не дубль: напомнить, что есть |
| `tests/` с `TransactionCase`/`HttpCase`, команда `odoo-bin … --test-tags` в README/CLAUDE.md | Setup-скрипт облачного окружения: PostgreSQL + Odoo 19 (исходники с пином ветки/коммита, `pip install -r requirements.txt`), чтобы тесты можно было запустить в сессии | Окружение облака | Минуты на первую сборку окружения, потом кеш. Без этого тесты в облаке не запустить — так и пиши в «Не проверено» |
| То же, но установка короткая | `SessionStart`-хук (скилл `session-start-hook`), только для быстрых шагов (`pip install -e`, создание БД) | Хуки | Время на каждом старте; хук должен молчать без своих данных |
| Тесты есть, хочется «тесты после правки» | НЕ хук на весь набор. По команде: `--test-tags /<модуль>` или `:TestClass.test_x` | — | Полный прогон Odoo — минуты: дорого как always-on |
| `.pre-commit-config.yaml` с `pylint-odoo`/`ruff` | `PostToolUse` (matcher `Edit|Write`) на изменённый `.py`: `ruff check <file>` / `pre-commit run --files <file>` | Хуки | Секунды на правку; нужен установленный инструмент в окружении |
| Нет линтера вовсе | Не придумывай хук; можно предложить добавить `ruff` в проект (решение людей) | — | |
| `security/ir.model.access.csv`, `@http.route(auth="public")`, `sudo()` | `security-review` (встроенный) / `anthropic-skills:security-review` по запросу перед деплоем | Скиллы | Уже есть — не дубль |
| Несколько модулей с `_inherit`, вопросы «кто расширяет» | `odoo-model-map` из `boost` (уже есть) | Скиллы | |
| `data/*.xml` с `noupdate="1"`, миграции `migrations/<версия>/` | `PreToolUse`-хук с подтверждением (`ask`) на правку `migrations/**` | Хуки | Мало срабатываний; полезен, если миграции правили по ошибке |
| Живая база Odoo нужна для данных | Коннектор `odoo-connector` (организации) — уже есть | MCP | Не ставить второй Odoo-MCP |

## Облако и уже применённые правила

| Признак | Рекомендация | Категория | Цена |
|---|---|---|---|
| `CLAUDE.md` ссылается на скиллы плагина (`boost`, `cloud-memory`), а `.claude/settings.json` нет или в нём нет `enabledPlugins` | Объявить маркетплейс и плагин в закоммиченном `.claude/settings.json` (`extraKnownMarketplaces`, `enabledPlugins`), если организация не ставит его сама | Плагины | Пара строк; без этого ссылка в `CLAUDE.md` в облаке «висит» |
| В `CLAUDE.md` «Пол качества» (запрет `# noqa`, `@skip`, `except: pass`), И в коде найдено нарушение (`path:line`) | `PreToolUse`-хук на Edit/Write: отклонить новую строку с этими маркерами (барьер вместо повторного текста; правила в `CLAUDE.md` не трогать). Без найденного нарушения не советуй | Хуки | ~10–50 мс на правку; ложные срабатывания на легитимных `noqa` — нужен путь «спроси человека» |

## Общие признаки

| Признак | Рекомендация | Категория | Цена |
|---|---|---|---|
| Нет `CLAUDE.md` | `templates/CLAUDE.md` + 3–5 строк о стеке и командах тестов/линтера | CLAUDE.md | ~600–700 токенов в каждой сессии |
| `CLAUDE.md` есть, но без команды тестов/линтера | Дописать 1–2 строки (команда из README/CI) | CLAUDE.md | Пара строк |
| `.env`, `*.pem`, `secrets*` в рабочем дереве | `PreToolUse`-хук `deny` на Edit/Write этих путей | Хуки | ~10 мс на правку |
| `poetry.lock`, `package-lock.json`, `uv.lock` | `PreToolUse`-хук `ask`/`deny` на ручную правку lock-файла | Хуки | ~10 мс |
| ruff/black в `pyproject.toml` | `PostToolUse`: `ruff format <file>` / `ruff check --fix <file>` | Хуки | Секунды; только изменённый файл |
| Prettier/ESLint/tsc в `package.json` | `PostToolUse`: `prettier --write <file>`, `eslint <file>`; `tsc --noEmit` — только по команде на больших проектах | Хуки | tsc на каждую правку дорог |
| Повторяемая процедура проекта (релиз, миграция, выгрузка) описана в README | Свой скилл в `.claude/skills/<имя>/` с `disable-model-invocation: true` для действий с побочными эффектами | Скиллы | Только описание в контексте |
| Много постоянных разрешений в сессиях | `fewer-permission-prompts` (встроенный) — allowlist по транскриптам | Настройки | Уже есть — запустить, а не писать вручную |
| Ссылки на Jira/Atlassian, Linear, Sentry | Соответствующий коннектор claude.ai (если ещё не подключён в сессии) | MCP | Авторизация организации |
| UI на фронтенде с e2e-тестами | Playwright MCP | MCP | В облаке Chromium предустановлен, но MCP — отдельный процесс |
| `memory/` нет, работа многосессионная | `cloud-memory` из `boost`: создать `memory/INDEX.md` — хуки плагина уже его подхватят | Память | ~10 мс на старте, ≤ 9 КБ контекста |
| PostgreSQL/MySQL, нужны запросы | Database MCP — только с read-only пользователем и не на прод | MCP | Риск данных; спросить людей |

## Субагенты

Рекомендуй, только если у проекта есть особые правила, которых нет у
встроенных ревьюеров (например, «проверка `ir.rule` по матрице ролей
проекта»), и это часто. Общие `code-reviewer`/`test-writer`/
`security-reviewer` — дубль встроенных `code-review`, `security-review`
и `repo-audit`; субагенты в 1.5–5 раз дороже обычного ответа.

## Частые неточности оригинала (не повторять)

- `claude mcp add context7` без URL — неполная команда; рабочая:
  `claude mcp add --transport http --scope user context7 https://mcp.context7.com/mcp --header "Authorization: Bearer $CONTEXT7_API_KEY"`
  или `.mcp.json` из шаблона.
- Флага `--mcp-debug` не советуй; для диагностики — `/mcp`, `claude --debug`.
- Уведомления `osascript`/`afplay` бесполезны в облаке.
