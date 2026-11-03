# Odoo Agent Pro Kit

- **Тип:** плагин (31 скилл, 5 команд, хуки на 7 событий, MCP-сервер) + Docker-песочница и установщики
- **Источник:** https://github.com/infovpcs/odoo-agent-pro-kit (★8, Apache-2.0 + NOTICE)
- **Версия / коммит:** плагин 0.8.2, коммит `99515dbc3526e6877cccb5f8a0de3b7bd1050574` (2026-10-29)
- **Лицензия:** Apache-2.0, файл `NOTICE` (Copyright 2026 Vinay Rana) — при дословном переносе нужны атрибуция, копия лицензии и текст `NOTICE`
- **Дата разбора:** 2026-11-03
- **Вердикт:** адаптировать (выборочно: линтер ловушек и проверенные факты Odoo 19); как плагин — не ставить

## Что делает

Набор VPCS для разработки модулей Odoo 17/18/19/20 агентами (Claude Code, Codex,
Cursor, Copilot, Hermes, DeepSeek): цикл `/plan-analysis` → `/start-coding` →
`/testing`, скиллы стандартов кода по версиям, тестирования, документации,
миграции, fit-gap анализа; детерминированные хуки (линтер версионных ловушек,
запрет `odoo-bin`/`git push` без разрешения, защита от записи секретов и
Enterprise-кода, ворота между шагами); MCP для метаданных моделей; локальный
bootstrap Odoo и Docker Sandbox на модуль.

**Гипотеза** «набор для разработки модулей Odoo 17–20» подтверждается. Но это
не компактный набор скиллов, а платформа под окружение автора
(`~/odoo-workspaces`, порты 8765–8768, `manage_modules.sh`, microVM).

## Какую слабость Claude закрывает

Факты новой версии Odoo — ровно нашу главную слабость (`synthesis.md`, п. 3).
Лучшее решение у них — не текст, а **барьер**: PostToolUse-линтер, который
после каждой записи файла модуля находит `<tree>`, `attrs=`, `type='json'`,
`<group expand>` в поиске, `res.groups.category_id` и возвращает модели ошибку
с исправлением.

## Как устроен

- `plugin/skills/` — 31 скилл, 7449 строк; описания всех ≈ 7.5 тыс. символов
  (≈ 2 тыс. токенов всегда). Крупные: `Agent-browser-skill` 1117, скриншоты 730,
  тесты 663/640, `Odoo19CodingStandard` 443.
- `plugin/hooks/` — `odoo_hook.py` + `checks/` (lint L1–L18, guard, paths, gates),
  fail-open, молчат вне Odoo-модуля.
- `plugin/odoo_mcp/` — 7 read-only инструментов, в `plugin.json` не
  регистрируется, стартует вручную.
- Сеть: только локальный Odoo. Телеметрии нет. В текстах скиллов есть
  `curl … | sh` (uv) и `pip install` как инструкции агенту.

## Сводка по частям

| Часть | Что | Вердикт | Итого | Карточка |
|---|---|---|---|---|
| Хуки + `odoo_lint` | Барьер на версионные ловушки, guard VCS/секретов, ворота шагов | адаптировать линтер | 11/18 | [`items/odoo-lint-hooks.md`](items/odoo-lint-hooks.md) |
| `Odoo19CodingStandard` (+ `OdooTools19`, `DependencyContext`) | Справочник правил 19 | адаптировать проверенные факты | 10/18 | [`items/Odoo19CodingStandard.md`](items/Odoo19CodingStandard.md) |
| `OdooRequirementGapAnalysis` | ТЗ → fit-gap с проверкой модулей по коду | идеи владельцам пресейла/ТР | 10/18 | [`items/OdooRequirementGapAnalysis.md`](items/OdooRequirementGapAnalysis.md) |
| Команды + `CommandingSystem` + `odoo_mcp` | Цикл plan → code → test, песочницы | отклонить (дубль `odoo19-mvp-build`, `odoo-connector`) | 8/18 | [`items/lifecycle-commands.md`](items/lifecycle-commands.md) |
| Прочие: тесты фронта/бэка, скриншоты, браузер, POS/Web/Website/Migration-персоны, excalidraw, PRD-Writing, 17/18/20-скиллы, Hermes/DeepSeek | | не разбирали подробно: вне нашего стека или дубль | — | — |

## Точность по Odoo 19 (выборочно, детали в `notes.md`)

7 утверждений верны (группы `privilege_id`/`user_ids`, `<group>` без `expand`,
`jsonrpc` с 19.0, `ir.cron`, `allow_none=False`, `compute_sql` нет в 19.0,
параметры `@route`). Ошибки: L3 советует `jsonrpc` на 18.0 (там его нет);
`<act_window>` в RNG-разделе; L6 не знает, что `_sql_constraints` в 19
игнорируется; `OdooTools19` ссылается на несуществующие файлы. Нашу ловушку
`res.partner.mobile`/`title` кит не ловит.

## Проверка

A/B не проводилась (внешний код не запускаем без разрешения).

| Задача | Без него | С ним |
|---|---|---|
| — | — | — |

## Оценка (кит целиком)

| Критерий | Балл (0–3) | Комментарий |
|---|---|---|
| Прирост | 1 | Сильный линтер, остальное дублирует наши плагины; не измерено |
| Частота | 2 | Разработка модулей — каждую неделю |
| Надёжность | 1 | Ошибки в фактах, мусор в `OdooTools19`, работает только в их окружении |
| Стоимость контекста | 1 | ≈ 2 тыс. токенов описаний всегда + хуки на каждый Bash/Edit; workflow по 400–700 строк |
| Безопасность | 2 | Код хуков прочитан, сети наружу нет; но guard блокирует наш `git push`, установщики в текстах, MCP `0.0.0.0` в песочнице |
| Поддержка | 2 | 200 коммитов за 3.5 мес., CI, тесты; один вендор |
| **Итого** | **9/18** | |

## Что и куда перенести

SHA везде `99515db` (полный — в шапке). Лицензия Apache-2.0 разрешает всё ниже;
для дословного переноса — `references/ATTRIBUTION.md` с URL, SHA, текстом `NOTICE`
и пометкой «изменено».

| # | Исходный файл (`путь@SHA`) | Что берём | Куда у нас | Как | Лицензия |
|---|---|---|---|---|---|
| 1 | `plugin/hooks/checks/odoo_lint.py@99515db` | Регэкспы правил L1, L2, L3 (только 19), L4, L5; приём «вырезать комментарии → определить тип файла по пути → серьёзность по версии → сообщение + исправление» | новый `plugins/boost/skills/odoo19-lint/scripts/lint.py` | регэкспы дословно с атрибуцией (короткие, проще не переписывать); остальной код свой; свои правила: `_sql_constraints`, `res.partner` `mobile`/`title`, `res.groups.users`, `ir.cron` `numbercall`/`doall`, `view_mode` с `tree`, `self._context` | да, Apache-2.0 с атрибуцией и NOTICE |
| 2 | `plugin/hooks/odoo_hook.py@99515db` (`_handle_post_tool`), `plugin/hooks/hooks.json@99515db` | Схема PostToolUse на `Write\|Edit\|MultiEdit`, fail-open, молчание вне модуля | `plugins/boost/skills/odoo19-lint/` + `plugins/boost/hooks/` (опционально, только warn) | только идея, код свой | да |
| 3 | `plugin/skills/Odoo19CodingStandard/SKILL.md@99515db` (разделы «Odoo 19 Security Model», «Search View `<group>`», «Compute methods… `NewId`», «Controllers And Routes») | Факты: `privilege_id`/`user_ids`, поиск без `expand`/`string`, `counts.get(rec.id, 0)`, чек-лист ревью `@route` | `plugins/boost/skills/lean-change/references/odoo19.md` | пересказ своими словами, каждый факт с цитатой из исходника 19.0 (не из кита) | да (факты не охраняются; при пересказе атрибуция как источник идеи) |
| 4 | `plugin/skills/OdooRequirementGapAnalysis/SKILL.md@99515db` (Phase 0, Phase 2), `…/scripts/verify_modules.py@99515db` | Входной контроль ТЗ (11 пунктов), проверка технических имён модулей по `__manifest__.py`, таблица доказательств для Fit | предложение владельцам `odoo19-sales-prep` / `odoo19-tr-authoring` (файл `proposals/…` — по решению главной сессии) | только идея / пересказ; скрипт не берём (не читали целиком) | да |
| 5 | `plugin/hooks/checks/gates.py@99515db`, `_handle_stop` в `odoo_hook.py@99515db` | Ворота между шагами хуком («Record only what the tests showed») | никуда сейчас; в `observations/`, если `odoo19-mvp-build` начнёт пропускать шаги | только идея | да |

Не берём: команды и `CommandingSystem`, `odoo_mcp` (дубль `odoo19-mvp-build` и
`odoo-connector`), `guard.py` (блокирует наш `git push`), `OdooTools19` (ошибки).

## Риски и заметки

- Не устанавливать плагин в облачные сессии: guard блокирует `git push` внутри
  Odoo-модуля (наш обязательный шаг), Stop-хук может держать сессию.
- Не открывать клон как проект Claude Code: корневой `.claude/settings.json`
  запускает `scripts/contributor_hook.py`.
- Сравнение с `odoo19-mvp-build:scaffolding`/`code-dev` — только по назначению,
  тексты в контейнере недоступны (см. `notes.md`).
