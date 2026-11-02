# Рабочий журнал: claude-code-setup

## Источник

- Страница маркетплейса: https://claude.com/marketplace/plugins/claude-code-setup
  (метка «Anthropic verified», 195 067 установок на 2026-11-02, команды
  установки нет, только кнопка «Install in Claude Code»).
- Исходный код: https://github.com/anthropics/claude-plugins-official,
  папка `plugins/claude-code-setup`.
- Коммит репозитория: `a7ba5b93db0c7c8d17f3f1d25853adca79598a1a`
  (2026-10-30). Страница маркетплейса ссылается именно на этот коммит.
- Версия в `plugin.json`: `1.0.0`. Автор: Anthropic, по README Isabella He.
- Лицензия: Apache 2.0. Поэтому копии `SKILL.md` и `plugin.json` лежат
  в `source/` без изменений.
- Запись в `.claude-plugin/marketplace.json`: `category: productivity`,
  `source: ./plugins/claude-code-setup`.
- Клон в scratchpad (`--depth 1`), вне нашего репозитория. Ничего не
  запускали.

## Что смотрели

| Файл | Строк | Что внутри |
|---|---|---|
| `.claude-plugin/plugin.json` | 9 | Манифест: имя, описание, версия 1.0.0 |
| `README.md` | 29 | Описание и примеры фраз-триггеров |
| `skills/claude-automation-recommender/SKILL.md` | 289 | Сам скилл |
| `references/mcp-servers.md` | 276 | Каталог MCP: признак в коде → какой сервер рекомендовать |
| `references/skills-reference.md` | 408 | Шаблоны своих скиллов, справка по frontmatter |
| `references/hooks-patterns.md` | 226 | Паттерны хуков: форматтеры, линтеры, защита файлов, уведомления |
| `references/subagent-templates.md` | 181 | Шаблоны субагентов: ревьюеры, test-writer и др. |
| `references/plugins-reference.md` | 97 | Список официальных плагинов, включая LSP |
| `automation-recommender-example.png` | — | Скриншот для README |

Всего около 1 700 строк markdown. Скриптов, хуков, MCP-серверов, агентов
и команд нет.

## Проверка безопасности

- Исполняемого кода нет. `grep` по `curl|wget|rm -|sudo|eval|base64`
  ничего не нашёл.
- Скилл просит выполнить через Bash только `ls` и `cat` файлов
  проекта (`package.json`, `.claude/`, `CLAUDE.md`).
- Во frontmatter стоит `tools: Read, Glob, Grep, Bash`. Это
  нестандартное поле: для скиллов стандартное `allowed-tools`, так что
  ограничение, скорее всего, не действует. Режим «только чтение»
  держится на тексте инструкции, а не на правах.
- Сеть: скилл прямо предлагает «use web search» для рекомендаций под
  стек. Наружу уходят поисковые запросы с именами библиотек проекта.
  Код и секреты в них не попадают.
- Настройки и файлы скилл сам не меняет. Он только печатает отчёт.

## Наблюдения о качестве

- Сильный уклон в JS/фронтенд (React, Prettier, Jest, Supabase, Convex).
  Для Python есть ruff/black/mypy/pytest/pyright. Odoo не упомянут.
- Есть неточности и устаревшие места:
  - `claude mcp add context7` в шаблоне отчёта — неполная команда, у
    неё нет URL или команды запуска сервера;
  - `--mcp-debug` и `/plugin info` под вопросом (вероятно, устарели);
  - в `hooks-patterns.md` таблица «Quick Reference» повторяется дважды;
  - примеры уведомлений рассчитаны только на macOS (`afplay`,
    `osascript`) и бесполезны в облачной сессии.
- Скилл проверяет только `.claude/` и `CLAUDE.md`. Уже установленные
  плагины, скиллы и коннекторы он не учитывает, поэтому может
  предложить то, что у нас уже есть (code-review, GitHub MCP, docx/pdf).
- Хорошее: компактная таблица «признак в репо → автоматизация» по пяти
  категориям, разумное правило «1–2 рекомендации на категорию», справка
  по frontmatter скиллов (`disable-model-invocation`, `user-invocable`,
  `context: fork`, `` !`cmd` `` для подстановки вывода команды).

## Сравнение с нашими встроенными скиллами

| Наш скилл | Что делает | Пересечение с claude-code-setup |
|---|---|---|
| `init` | Пишет `CLAUDE.md` по кодовой базе | Нет: recommender не пишет `CLAUDE.md` |
| `update-config` | Меняет `settings.json`: хуки, права, env | Recommender советует хуки, а внедрять их — это работа `update-config` |
| `fewer-permission-prompts` | Строит allowlist по транскриптам | Нет; у recommender есть только общий пример `permissions.allow` |
| `session-start-hook` | SessionStart-хук для облачных сессий | Recommender про SessionStart не знает |
| `plugin-authoring` | Моды интерфейса и хуки | Слабое |

Чего у нас нет и что даёт плагин: единый «аудит» репозитория с ответом
на вопрос «какие автоматизации Claude Code тут уместны» по всем пяти
категориям сразу. Но это знание-шпаргалка, а не новая возможность:
Claude без скилла даст похожий список, только менее структурированный.

## Решения

- Предварительный вердикт: **адаптировать**. Ставить как есть можно для
  разового аудита (вреда нет), но пользы для Odoo/Python-стека и
  облачных сессий мало. Лучше свой скилл `repo-automation-audit`:
  таблица признаков из оригинала + наш стек (pylint-odoo, pre-commit,
  odoo-connector, session-start-hook) + сверка с `inventory/current.md`.

## Открытые вопросы

- Прогнать скилл на реальном репозитории (Odoo-модуль) и сравнить с
  ответом без скилла. Нужно разрешение пользователя на установку.
- Проверить актуальность `--mcp-debug`, `/plugin info` и команды
  установки context7.
