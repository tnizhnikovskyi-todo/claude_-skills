# Semia — рабочий журнал

Сессия анализа, ветка `analysis/semia`. Дата: 2026-11-03.

## Что смотрели

- Клон `berabuddies/Semia` в scratchpad, `HEAD` = `379bc25fe99833eb185efe56a38fe15f0235799c`
  (2026-06-05, «release: align v0.1.3 metadata»). Ничего не запускали: ни CLI,
  ни тесты, ни хуки pre-commit, ни `semia.pyz`.
- `LICENSE` — полный текст Apache-2.0; `NOTICE` — RiemaLabs; `TRADEMARKS.md` —
  имя «Semia» нельзя использовать в названии форков/производных.
- Прочитано: `README.md`, `prepare.py`, `schema.py`, оба `.dl` с правилами,
  `pipeline.py` (промпт синтеза), `llm_providers.py`, плагин Claude Code
  (`plugin.json`, `SKILL.md`), маркетплейс.
- `semia.pyz` (бандл в плагине) распакован через `zipfile` без запуска:
  33 файла, все побайтно совпадают с `packages/*/src` на этом SHA; бандлы
  claude-code и codex идентичны.

## Ход разбора

(дополняется ниже)
