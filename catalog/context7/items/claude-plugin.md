# Плагин Claude Code `context7` (`plugins/claude/context7`)

- **Тип:** плагин Claude Code (маркетплейс `context7-marketplace`)
- **Источник:** https://github.com/upstash/context7/tree/master/plugins/claude/context7
- **Версия / коммит:** 1.0.4, `18d6f5d`
- **Дата разбора:** 2026-11-02
- **Вердикт:** **взять** для локальной машины разработчика; для облака и CI использовать прямой MCP с ключом

## Что внутри

Всего три файла: `plugin.json`, `README.md` и `.mcp.json`:

```json
{ "mcpServers": { "context7": { "type": "http",
  "url": "https://mcp.context7.com/mcp?client=claude-code-plugin" } } }
```

Ни скиллов, ни хуков, ни команд, ни локального кода. По сути это только
закладка на удалённый MCP-сервер.

## Аутентификация

Только OAuth через `/mcp` → вход в браузере. Переменную `CONTEXT7_API_KEY`
плагин не читает (так и написано в его README). Поэтому в headless-, SSH-,
облачных сессиях и CI он неудобен: там лучше прописать сервер вручную с
заголовком `Authorization` (см. README папки).

## Установка

```bash
claude plugin marketplace add upstash/context7
claude plugin install context7@context7-marketplace
# перезапуск, затем /mcp → Context7 → Sign in
```

## Оценка

Как у `context7-mcp`, потому что это тот же сервер. Безопасность самого
плагина 3: он прозрачен и ничего не запускает локально. Минус один: маркетплейс
`upstash/context7` может обновить `.mcp.json` в будущих версиях. Ставить с
фиксированной версией или пересматривать при обновлении.
