# Рабочий журнал: ponytail

## 2026-11-02: первичный разбор

**Что смотрели**

- Клон `https://github.com/dietrichgebert/ponytail` в scratchpad, коммит
  `96608e0` (v5.3.3, 2026-10-29). Первый коммит 2026-06-12, 369 коммитов,
  137 авторов, MIT. Ничего не запускали.
- Полностью прочитаны все 6 `skills/*/SKILL.md`, манифесты
  `.claude-plugin/plugin.json`, `marketplace.json`, `hooks/claude-codex-hooks.json`,
  `hooks/claude-band.json`.
- Хуки: прочитаны `ponytail-activate.js` (до нуджа statusline), начало
  `ponytail-map.js`, `ponytail-subagent.js`, функции `record`/`writeBoard`/
  `openBoard`/`start` в `band/register.tsx`, `webhookRequest` в `band/metrics.ts`.
  По остальному коду grep на `http`, `fetch`, `child_process`, `exec`, `spawn`,
  `writeFile`, `unlink`, `eval`, `new Function`, env-переменные.
- Бенчмарк `benchmarks/results/2026-10-07-agentic.md` (раздел методики и таблицы).

**Что проверили / вывод по безопасности**

- Единственный исходящий запрос: опциональный webhook в band, только https
  (http лишь на localhost), токен в keychain. По умолчанию URL пустой.
- Внешних CDN, телеметрии, `eval` не найдено. Зависимостей нет (только Node).
- Запись: `~/.claude/.ponytail-active`, `~/.claude/ponytail-statusline.sh`,
  `~/.claude/.ponytail-statusline-nudged`, `~/.config/ponytail/` (config, CSV, board.html).
- Неприятный момент: SessionStart-хук в скрытом контексте просит модель
  прописать statusLine в `~/.claude/settings.json` (один раз).
- `band import` в фоне читает все `~/.claude/projects/*.jsonl` (локально, для board).
- `ponytail-map.js`: `git ls-files` + чтение исходников, только локально.

**Наблюдения**

- Ценность почти целиком в текстах скиллов (≈ 3.5 + 5 + 5.4 КБ), их можно
  взять без хуков.
- Пересечение с встроенными `code-review` и `simplify`. Уникальное: работа
  *до* кода (лестница переиспользования), финальная строка рисков, аудит
  целого репо, конвенция `shortcut:`.
- Бенчмарк собственный: качество не растёт, а сохраняется при −53% кода,
  −26% стоимости; тесты на рискованную логику 98% vs 68%. Судья LLM.
- Band не работает в облачных сессиях (по README автора).

## Открытые вопросы

1. Прогнать A/B на нашей задаче: Odoo-модуль из `odoo19-mvp-build` с правилами
   ponytail в CLAUDE.md и без. Нужно разрешение пользователя и тестовая задача.
2. Как правила ponytail уживаются с ТР-процессом, где объём зафиксирован
   клиентом (особенно уровень `ultra`)?
3. Брать `ponytail-audit` как есть или сразу делать Odoo-вариант?
4. Нужна ли нам «карта кода» на старте сессии (идея из `ponytail-map.js`)?
