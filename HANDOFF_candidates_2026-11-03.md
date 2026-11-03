# Передача: новые кандидаты на разбор (03.11.2026)

Для главной сессии (роль «хаб» по `CLAUDE.md`). Список собран поиском по GitHub (`gh api search/repositories`,
`pushed:>2026-06-01`, сортировка по звёздам). Смотрели **только описания и метаданные**, код и `SKILL.md`
не открывали, ничего не запускали. Оценки ниже — гипотезы, проверить в разборе по `criteria.md`.

Уже в каталоге (`catalog/INDEX.md`, 17 шт.) — исключены.

## Что сделать

1. Спросить пользователя, какие номера брать (по умолчанию — «первыми» 1–3).
2. На каждый выбранный: сессия анализа с `outcome_branch: analysis/<slug>`, строка в `sessions.md`
   (статус `в работе`). Слаги предложены в таблице.
3. В первом сообщении сессии анализа: slug, ссылка, «чем может помочь» из таблицы, с какими нашими
   скиллами сравнивать. Напомнить: чужой код недоверенный, не запускать; при отсутствии лицензии —
   только идеи своими словами.

## Кандидаты

| № | slug | Репозиторий | ★ | Лицензия | Чем может помочь | Сравнить с |
|---|---|---|---|---|---|---|
| **Первыми** |||||||
| 1 | `nacl` | [ITSalt/NaCl](https://github.com/ITSalt/NaCl) | 28 | MIT | 57 скиллов полного цикла: бизнес-анализ → архитектура → код | цепочки `odoo19-discovery-*`, `odoo19-tr-authoring`, `odoo19-mvp-build` |
| 2 | `dooservice-odoo-skills` | [dooservice/odoo-skills](https://github.com/dooservice/odoo-skills) | 2 | LGPL-3 | по описанию — скиллы самой Odoo 20.0, адаптированные под 16–20; проверить, правда ли первоисточник | `code-dev`, `pr-review`, `testing`, `boost:source-check` |
| 3 | `lmty-skills` | [LMTYdotcom/skills](https://github.com/LMTYdotcom/skills) | 84 | MIT | battlecards, win-loss, позиционирование, ценообразование | `defence-brief`, `loss-pattern-analyzer` |
| **Тоже подходят** |||||||
| 4 | `unclecatvn-skills` | [unclecatvn/agent-skills](https://github.com/unclecatvn/agent-skills) | 150 | MIT | документация Odoo в виде скиллов | `code-dev`, `boost:odoo-model-map` |
| 5 | `odoo-agent-pro-kit` | [infovpcs/odoo-agent-pro-kit](https://github.com/infovpcs/odoo-agent-pro-kit) | 8 | Apache-2.0 | набор для разработки модулей Odoo 17–20 | `scaffolding`, `code-dev` |
| 6 | `kevinlin-skills` | [kevinlin/skills](https://github.com/kevinlin/skills) | 5 | MIT | от gap-анализа требований до сданного кода | `discovery-gap-analyzer`, `spec-writer` |
| 7 | `erpipe-mcp-odoo` | [erpipe-org/mcp-odoo](https://github.com/erpipe-org/mcp-odoo) | 427 | MIT | MCP Odoo: запись через подтверждение, несколько баз | наш `odoo-mcp` |
| 8 | `planning-with-files` | [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) | 27.9k | MIT | план и состояние в файлах для долгих задач | `build-orchestrator`, `boost:cloud-memory` |
| 9 | `skillopt` | [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt) | 18.9k | MIT | автоматическое улучшение текстов скиллов | `boost:skill-feedback`, `observations/` |
| **Только идеи (лицензии нет)** |||||||
| 10 | `mart337i-odoo-skills` | [mart337i/odoo-skills](https://github.com/mart337i/odoo-skills) | 61 | нет | справочник Odoo 19 (18 руководств), ревью, тесты | `pr-review`, `testing` |
| 11 | `odoo-lens` | [ChengyanOo/odoo-lens](https://github.com/ChengyanOo/odoo-lens) | 21 | нет | линтер/LSP для Odoo 16–20 | `pr-review` |

№ 10–11 уже предварительно смотрели в `tnizhnikovskyi-todo/todo_timur`: реестр
`factory3d/tools/external/README.md` и `factory3d/build/HANDOFF_external_tools.md`
(ветка `claude/bold-bell-5okjhm` того репозитория). Закреплённые коммиты: odoo-lens `2482f92`,
odoo-skills `634b2db`.

## Отброшено

- `stanleykao72/claude-code-spec-workflow-odoo` (MIT): дублирует наши SPEC/ARCHITECTURE, заброшен с 09.2025.
- `ivnvxd/mcp-server-odoo` (MPL-2.0): есть свой `odoo-mcp`; при желании сравнить вместе с № 7.
- Холодные рассылки (`growthenginenowoslawski/coldoutboundskills`, `explorium-ai/gtm-skills` и т. п.):
  у нас продажа через бриф и демо, не рассылки.

Поиск продолжается в чате-источнике; новые находки — дописывать сюда.
