# Отчёт: задача 4.3 `automation-audit`

Ветка `build/automation-audit`. Основа: разбор `catalog/claude-code-setup/`
(официальный плагин Anthropic, скилл `claude-automation-recommender`,
Apache 2.0, см. `notes.md`). Текст не копировался дословно: схема фаз,
правило «1–2 на категорию» и скелет таблиц признаков пересказаны и
переписаны, атрибуция и список изменений в
`plugins/boost/skills/automation-audit/references/attribution.md`
(п. 4(b) Apache 2.0).

## Что сделано и где

| Путь | Что |
|---|---|
| `plugins/boost/skills/automation-audit/SKILL.md` (~135 строк) | Узкий триггер: «что автоматизировать», «аудит настройки Claude Code», «automation audit», «какие хуки/скиллы/MCP поставить»; не для настройки конкретного хука (`update-config`), объяснения настройки, `init`, аудита кода (`repo-audit`). Шаги: профиль (включая Odoo: `__manifest__.py` 19.0, `odoo-bin`, `TransactionCase`/`@tagged`) → **обязательный раздел «Уже есть»** (`CLAUDE.md`, `.claude/`, `.mcp.json`, `memory/`, скиллы сессии, `inventory/current.md`, `boost`) → облачная сессия (эфемерный контейнер, setup-скрипт vs `SessionStart`, плагины через `enabledPlugins`, секреты окружения) → что рекомендовать/нет (выводы `synthesis.md`) → отчёт: у каждой рекомендации Что / Зачем / Подтверждено (путь) / Цена, ≤ 2 на категорию, «Не рекомендую», «Не проверено». Только чтение |
| `.../references/signals.md` | Таблица «признак → автоматизация → цена» для Odoo 19/Python, облака и общих признаков; когда субагенты — дубль; неточности оригинала, которые не повторять (`claude mcp add context7` без URL, `--mcp-debug`, macOS-уведомления) |
| `.../references/known-setup.md` | Что уже есть: скиллы `boost`, встроенные, организации, коннекторы — с колонкой «дубль, если советуешь…»; признаки применённого `templates/CLAUDE.md` и `templates/mcp.json` |
| `.../references/attribution.md` | Источник, лицензия, что взято и что изменено |
| `plugins/boost/evals/automation-audit/_fixture/pilot/` | Копия `pilot/` (Odoo 19, шаблон `CLAUDE.md` применён без раздела Context7; нет `.mcp.json`, `.claude/`, `memory/`) |
| `plugins/boost/evals/automation-audit/_fixture/py-service/` | FastAPI + uv + alembic + Stripe; уже есть `PostToolUse`-хук `ruff format` и Context7 в `.mcp.json`; нет `CLAUDE.md`; `setup.sh` кладёт `.env` с фейковым ключом |
| `plugins/boost/evals/automation-audit/{odoo-pilot,py-service,explain-negative}/` | 3 кейса |

`claude plugin validate plugins/boost`: проходит.

## Чем отличается от оригинала

| Оригинал | `automation-audit` |
|---|---|
| Таблицы под JS/фронтенд, Odoo нет | Признаки Odoo 19 и Python: Context7 c `/websites/odoo/19.0`, setup-скрипт PostgreSQL + Odoo для `--test-tags`, pylint-odoo/ruff по одному файлу, `noupdate`/миграции, `odoo-connector`, `odoo-model-map` |
| Не видит установленного, предлагает дубли | Раздел «Уже есть» обязателен; таблица дублей; «шаблон применён» распознаётся по разделам |
| Нет облака | Эфемерный контейнер, setup-скрипт vs `SessionStart`, плагины через `.claude/settings.json`, секреты окружения |
| «Why» и «Where» | Зачем / Подтверждено путём / Цена; раздел «Не рекомендую»; запрет always-on тестов и общих субагентов |
| Веб-поиск под стек | Без сети |

## Eval-кейсы

| Кейс | Запрос | Что проверяют грейдеры (sonnet) |
|---|---|---|
| `odoo-pilot` | «что автоматизировать… облачные сессии» на копии `pilot/` | `template-applied`: признаёт правила шаблона, не советует `/init`/те же правила; `no-duplicates`: нет Memory MCP, общих ревьюер-субагентов, GitHub/второго Odoo MCP, скилла поиска наследований; `cloud-odoo`: setup/SessionStart для Odoo 19 + PostgreSQL со ссылкой на признак и без хука «все тесты после правки»; `evidence-and-cost` |
| `py-service` | «automation audit… облачные сессии» | `sees-existing`: хук ruff и Context7 отмечены и не предложены снова; `claude-md-and-guards`: `CLAUDE.md` с командами + защита `.env`/lock/миграций; `cloud-setup`; `evidence-and-cost` |
| `explain-negative` (негатив) | «что делает хук в `.claude/settings.json`» | скилл не сработал; ответ — объяснение, не аудит |

`tool_used: Skill` в оценку не входит (индикатор).

## Результат A/B

```bash
claude plugin eval plugins/boost --case 'automation-audit/*' --runs 3 --max-cost-usd 6 \
  --no-publish --scaffold --trust-plugin -j 4 --judge-model sonnet --threshold 0
```

| Кейс | С плагином | Без | Δ | Скилл сработал |
|---|---|---|---|---|
| `odoo-pilot` | 1.00 | 0.17 | **+0.83** | 3/3 |
| `py-service` | 1.00 | 0.75 | **+0.25** | 3/3 |
| `explain-negative` | 1.00 | 1.00 | 0 | 0/3 (так и надо) |
| **Среднее** | 1.00 | 0.64 | **+0.36** | |

Стоимость прогона: **$4.16** (оба плеча и судья), 173 с. Агент: $0.31–0.37
на аудит со скиллом против $0.17–0.41 без (примерно одинаково, скилл даёт
+3–8 ходов на чтение `references/`); судья sonnet ~$0.2 на аудит-отчёт.

### Что решило

- **`odoo-pilot`, база 0/3 по трём грейдерам из четырёх.** Без скилла
  модель видит «пол качества», но не понимает, что это применённый шаблон,
  и предлагает переписать/расширить `CLAUDE.md`; советует свой субагент
  `odoo-reviewer`, скиллы `odoo-module-check`/`odoo19-api-notes`, GitHub MCP
  и `Stop`-хук, гоняющий тесты (дорогой always-on); у рекомендаций нет
  цены. Облако база учитывает сама (2/3): setup-скрипт Odoo + PostgreSQL.
  Со скиллом: «шаблон применён», `memory/INDEX.md` для уже установленного
  `cloud-memory` вместо нового механизма памяти, Context7 из
  `templates/mcp.json` с ценой (ключ, домены), явное «Не рекомендую» с
  дублями и хуком тестов.
- **`py-service`.** Существующий хук и Context7 база видит сама (3/3), как
  и защиту `.env` и облачную установку; падает только формат
  (подтверждение путём + цена у каждой рекомендации, ≤ 2 на категорию).
  Здесь прирост — дисциплина формата, как у `repo-audit`.
- **Негатив.** Вопрос про один хук скилл не трогает ни в одном прогоне.

### Находка базового плеча, перенесённая в скилл

Без скилла модель в 2/3 прогонов `odoo-pilot` заметила то, что пропустил
скилл: `CLAUDE.md` ссылается на `boost`/`cloud-memory`, а в облаке плагин
будет, только если его ставит организация или он объявлен в закоммиченном
`.claude/settings.json` (`extraKnownMarketplaces` + `enabledPlugins`).
Скилл со своей стороны писал «`boost` установлен», потому что видел себя в
сессии. Добавил пункт в раздел «Облачная сессия» и строку в `signals.md`,
вместе с хуком-барьером `PreToolUse` для «пола качества» (тоже идея
базы, совпадает с принципом 5.1 roadmap «второе нарушение лечится
барьером»).

<!-- CONTROL -->

## Что не получилось / ограничения

- Bash в eval закрыт (нет песочницы), поэтому скилл не смотрел `git log` и
  не проверял, установлены ли инструменты. Для аудита это нормально: всё
  нужное читается файлами.
- Кейсы с «чистым» стеком JS/фронтенд не делал: исходный скилл покрывает
  его, а у нас нет таких проектов.
- Грейдер `evidence-and-cost` проверяет формат, который задаёт сам скилл,
  поэтому база падает на нём закономерно; содержательный прирост — в
  `template-applied`, `no-duplicates` и частично `cloud-odoo`.
- `known-setup.md` — снимок на 2026-11-02; при изменении состава `boost`
  или `inventory/current.md` его нужно обновлять (или добавить
  напоминание в процесс 5.1).

## Открытые вопросы

1. Нужен ли прогон на настоящем рабочем Odoo-репозитории (не фикстуре),
   когда он появится (задача 0.2/0.3)?
2. Стоит ли в шаблоне `templates/` иметь готовый `settings.json` с
   `extraKnownMarketplaces`/`enabledPlugins` для `boost`? Скилл теперь
   советует это, но готового шаблона нет.

## Нужные правки общих файлов (для главной сессии)

- `plugins/boost/README.md`, таблица «Состав»: строка
  `| automation-audit | Аудит настройки Claude Code для репо: профиль (в т.ч. Odoo 19), раздел «Уже есть» без дублей boost/встроенных, облако (setup-скрипт, SessionStart, enabledPlugins), по 1–2 рекомендации с «Подтверждено» и «Цена». Только чтение | +0.36 в среднем (+0.83 на копии pilot, +0.25 на Python-сервисе); на негативе не срабатывает | 4.3 |`
- `plugins/boost/.claude-plugin/plugin.json`: в `description` добавить
  «аудит автоматизаций»; версия 0.4.0.
- `roadmap.md`: статус 4.3 — готово, отчёт `reports/automation-audit.md`.
- `templates/README.md` (по желанию): строка о
  `.claude/settings.json` с `enabledPlugins` для облачных сессий.
