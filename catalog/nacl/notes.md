# NaCl: рабочий журнал

## 2026-11-03 — первичный осмотр

- Клон: `ITSalt/NaCl`, HEAD `20fe4c6` (2026-09-28), 388 коммитов с 2026-04-10,
  один основной автор (Max Nikitin). Лицензия MIT. Плагин `nacl` 2.28.0.
- Размер 77 МБ: 1100 md, 282 mjs, 123 ts, 105 sh, 74 py, 42 cypher.
- В корне 59 скиллов `nacl-*` с `SKILL.md`: BA 14, SA 10, TL 26 (+`nacl-tl-core`
  без SKILL.md), утилиты, миграция. Гипотеза «57 скиллов полного цикла
  BA → архитектура → код» по сути подтверждается (59 корневых).
- **Ключевое:** всё держится на Neo4j-графе проекта (Docker-контейнер на
  проект + `neo4j-mcp`). Скиллы пишут/читают узлы через `mcp__neo4j__*`.
  Без графа BA/SA/TL-скиллы не работают.
- Размер скиллов: `SKILL.md` от 300 до 2909 строк (`nacl-sa-validate`),
  `nacl-sa-uc` ~15 тыс. слов, `nacl-goal` 25 тыс. слов с references.
  Наше правило — до ~150 строк.

## Безопасность (чтение кода, ничего не запускалось)

- `plugin/hooks/hooks.json`: `SessionStart` (startup|resume):
  `graph-doctor.mjs --hook` (618 строк) и `check-coexistence.sh` (10 строк).
  - `--hook` молчит, если в проекте нет конфигурации NaCl; при наличии —
    TCP-проба порта Neo4j; в remote-режиме **сам перезапускает SSH-sidecar**
    (launchctl / schtasks / detached spawn); при падении графа подмешивает
    `additionalContext` «граф DOWN, предложи --fix». Docker сам не поднимает,
    это делает `--fix` по согласию.
  - копирует `.mcp.json` в worktree.
- `monitors.json` (experimental): постоянный `graph-doctor --watch`.
- Сеть: GitHub (релизы `neo4j-mcp`, проверка чексумм), Docker-образы,
  опционально Docmost, YouGile. `NEO4J_TELEMETRY=false` выставляется явно.
  Своего бэкенда и телеметрии нет (`PRIVACY.md`), подтверждено grep-ом.
- `nacl-init` создаёт Docker-стек, пароль в `graph-infra/.env` (0600),
  правит `.mcp.json`/`.codex/config.toml`. Тяжёлые побочные эффекты, но
  с явным подтверждением.
- Вывод: злонамеренного нет, но footprint большой (Docker, бинарь MCP,
  SSH-туннели, хук на каждый старт).

## Наши скиллы для сравнения

- `~/.claude/plugins/synced/*/` пуст в этом контейнере. Тексты нашлись в
  `~/.claude/skills/synced/*/`: `tr-review` (109 строк),
  `tr-usecases-acceptance` (86), `tr-odoo-tech-design` (120),
  `odoo-spec-writer` (123), `session-transcript-analyzer` (267),
  `sales-handover-analyzer`, `meeting-protocol-builder`, `security-review`.
- Скиллов `odoo19-mvp-build` (code-dev, testing, pr-review) и большинства
  `odoo19-discovery-*` здесь нет; частично — в `proposals/` нашего репо.

## 2026-11-03 — разбор методов и сравнение

- Прочитаны: `nacl-ba-full` (фазы, ворота yes/redo/stop, `status: assumption`),
  `nacl-ba-validate` (L1–L8, XL1–XL5, severity, классификатор),
  `nacl-ba-handoff` (матрица трассировки), `nacl-sa-uc` (stories/detail/
  slices/errors/resilience, Phase 4.5 Runtime Contract),
  `nacl-tl-review` (ворота заглушек, nav-actions, Step 6 baseline),
  `nacl-tl-core/references/gate-fire-catalog.md` (G1–G11),
  `project-gap-closure.md` (strict-mode, запрещённые «успехи»),
  `nacl-postmortem`, CHANGELOG 2.28.0.
- Сравнено с `tr-review`, `tr-usecases-acceptance`, `tr-odoo-tech-design`,
  `odoo-spec-writer`, `session-transcript-analyzer` (из `~/.claude/skills/synced`),
  а также `proposals/odoo19-discovery`, `proposals/odoo19-mvp-build`.
- Активность: коммиты 2026-04: 37, 05: 69, 06: 87, 07: 179, 08: 4, 09: 12.
  Один автор. Часть методологии ушла в приватный репо (`meta/`).
- Решение: отклонить как есть, 5 методов в `items/`.

## Открытые вопросы

- A/B адаптированных вставок на фикстурах ТР: нужно решение пользователя.
- Владелец `odoo19-tr-authoring` / `odoo19-mvp-build`: вставки, как и
  прошлые, пойдут через `proposals/` (это зона главной сессии/реализации).
- Odoo-API для блокировок и postcommit в Runtime Contract не сверены:
  перед вставкой прогнать через `source-check` (Odoo 19).

## 2026-11-03 — правило главной сессии (п. 5 `CLAUDE.md`)

- Получено сообщение от главной сессии: в README карточки указывать URL, SHA,
  лицензию и дату, а в «Что взять» — `путь@SHA`, что берём, куда, как
  (дословно / пересказ / идея) и разрешение лицензии. README обновлён:
  полный SHA `20fe4c6a56482e85d3ea9a9ebaadb37206047e41`, MIT (ITSalt),
  таблица «Что взять» с источниками.

## 2026-11-03 — сверка с текстами маркетплейса

- По подсказке главной сессии: `add_repo` на чтение
  `todoltd/claude-methodology-marketplace` прошёл, shallow-клон в
  `/home/user/claude-methodology-marketplace` (HEAD `7acde05`), вне нашего репо.
  `register_repo_root` не вызывал: плагины оттуда в сессию не грузил.
  Из приватного репо в наш ничего не копировал, только пересказ.
- Прочитаны: `odoo19-mvp-build` (`pr-review` + `references/review-discipline.md`,
  `testing`, `code-dev`), `odoo19-tr-authoring` (`tr-review`,
  `tr-usecases-acceptance`, `tr-odoo-tech-design`),
  `odoo19-discovery-closeout` (`journal-to-tr-builder`, `discovery-gap-analyzer`),
  состав `boost`.
- Итог: две идеи сузились (Runtime Contract, трассировка), baseline почти
  покрыт, достижимость UI и постмортем остаются полностью новыми. Таблица
  в README, раздел «Сверка с текущими текстами».
- `odoo19-sales-*` (публичный `sale_todo_claude`) не смотрел: к NaCl
  отношения не имеет (в NaCl нет продаж).
