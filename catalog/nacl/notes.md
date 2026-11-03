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
