# CLI `ctx7` и скилл `find-docs` (`packages/cli`, `skills/`)

- **Тип:** CLI (npm `ctx7`) + скиллы `find-docs`, `context7-cli`, `context7-mcp` + правила `rules/*.md`
- **Источник:** https://github.com/upstash/context7/tree/master/packages/cli, `skills/`
- **Версия / коммит:** `18d6f5d`
- **Дата разбора:** 2026-11-02
- **Вердикт:** **отклонить** как способ подключения; **адаптировать** идею текста скилла

## Что делает

- `ctx7 setup` логинит через OAuth, создаёт API-ключ и для Claude Code пишет
  MCP-конфиг в `~/.claude.json` или `.mcp.json`, правило в `.claude/rules/`
  и скилл в `.claude/skills/`. Режим «CLI + Skills» обходится без MCP: агент
  сам вызывает в Bash `npx ctx7@latest library ...` и
  `npx ctx7@latest docs ...`.
- `ctx7 remove` откатывает изменения.
- Телеметрия: `POST context7.com/api/v2/cli/events` с именем команды и
  режимом (без запросов). Отключается `CTX7_TELEMETRY_DISABLED=1`.

## Почему отклонить

- `npx ctx7@latest` при **каждом** вызове скачивает и запускает последнюю
  версию чужого npm-пакета. Это supply-chain-риск, который MCP-вариант не несёт.
- Нужен Node 22.13+, а каждый вызов добавляет задержку на npx.
- Установщик сам правит конфиги Claude. Всё то же самое делается вручную
  тремя строками.

## Что взять

`skills/find-docs/SKILL.md` (около 7,9 КБ) — хороший образец триггера:
«используй даже для известных библиотек, если речь про API/версии/конфиг;
не используй для общего рефакторинга». `rules/context7-mcp.md` (около 1,7 КБ)
— короткое правило для `CLAUDE.md`. Из них можно собрать своё правило про
Odoo 19 (черновик в README папки).
