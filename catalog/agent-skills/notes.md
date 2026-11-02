# Журнал разбора: addyosmani/agent-skills

## 2026-11-02 — первичный разбор

### Что смотрели

- Клон `--depth 1`, затем история с 2025-01-01, в scratchpad (вне репо).
  Коммит `301b02b12bff98e4688e6984af6556802322bbde` (2026-11-01), версия плагина 0.6.15.
- Манифесты: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`,
  `plugin.json`, `.codex-plugin/`, `.agents/plugins/`.
- Все 24 `skills/*/SKILL.md`: frontmatter и размеры. Целиком прочитаны
  `doubt-driven-development`, `interview-me`, `code-review-and-quality`,
  `source-driven-development`, половина `constraint-driven-development`.
  У `debugging-and-error-recovery`, `code-simplification`,
  `test-driven-development`, `context-engineering` прочитаны только оглавления.
- Все скрипты и хуки: `hooks/*.sh`, `skills/idea-refine/scripts/idea-refine.sh`,
  `skills/constraint-driven-development/scripts/quality-gate.mjs`.
- `.claude/commands/review.md`, `agents/code-reviewer.md`, `evals/README.md`,
  `evals/skill-impact.md`.

Ничего из внешнего репозитория не запускали.

### Безопасность (проверено чтением)

- `.claude-plugin/plugin.json` подключает только `commands` и `skills`.
  **Хуки плагином не подключаются**, это отдельный опциональный шаг.
- `hooks/session-start.sh`: печатает `using-agent-skills/SKILL.md` в контекст
  через `jq`. Сеть не трогает. В комментарии сам автор не советует включать его
  в Claude Code (там скиллы и так маршрутизируются по description).
- `hooks/sdd-cache-pre.sh` / `-post.sh`: кэш WebFetch в `.claude/sdd-cache/`.
  Делает `curl -sI` (HEAD) на тот же URL, что и WebFetch, для проверки
  ETag/Last-Modified. Новых адресов не добавляет, но **отдаёт агенту
  закэшированный текст вместо свежего WebFetch** (exit 2 + stderr). Если файл
  кэша подменить, это готовый канал для инъекции. Нам не нужен.
- `hooks/simplify-ignore.sh`: на `Read` **переписывает файл на диске**,
  заменяя блоки `simplify-ignore-start/end` плейсхолдерами, и восстанавливает
  его на `Stop`. Задумано аккуратно (бэкапы, `.recovered`, блокировки), но если
  сессия упадёт, рабочее дерево останется испорченным. Не ставить.
- `idea-refine.sh`: делает `mkdir -p docs/ideas` и печатает JSON. Безобидно.
- `quality-gate.mjs`: только `readFileSync` отчёта semgrep/axe и подсчёт
  severity. Без сети и без exec.
- В текстах скиллов есть `npx …` (tsc, lhci, playwright, vercel) как примеры
  команд для проекта пользователя. Скрытых загрузок нет.
- `doubt-driven-development` предлагает вызывать внешние CLI (gemini, codex),
  но только после явного согласия пользователя, в read-only песочнице и через
  stdin. Сформулировано грамотно.
- `browser-testing-with-devtools` требует MCP `chrome-devtools` (`npx -y
  chrome-devtools-mcp`). Это отдельный сторонний пакет из npm.
- Инъекций, направленных на агента, в SKILL.md не нашёл. Наоборот, несколько
  скиллов прямо требуют считать внешние данные недоверенными.

Итог: безопасность 3 для самих скиллов (это чистый markdown). Хуки по
умолчанию выключены. Из них `simplify-ignore` и `sdd-cache` не ставить.

### Поддержка

- Первый коммит 2026-02-15. Коммитов по месяцам: 32, 36, 94, 46, 106, 82, 91,
  121, 198 (октябрь 2026). Автор Addy Osmani (Google Chrome), 404 коммита, ещё
  десятки контрибьюторов. Лицензия MIT.
- Есть свой эвал-контур: структурная валидация, TF-IDF-проверка триггеров
  (`run-evals.js --min-rank1 95`), поведенческие эвалы через headless `claude`,
  `claude plugin eval` с прогонами с плагином и без. Готовых цифр «с/без» в
  репозитории нет: `evals/skill-impact.md` содержит только пустую таблицу
  отклонённых правок.

### Стоимость контекста

- 24 скилла, в сумме около 340 КБ markdown (по 10–22 КБ на SKILL.md, примерно
  2,5–5,5 тыс. токенов каждый при срабатывании).
- Плагин целиком добавляет в постоянный контекст 24 description по 300–900
  символов, то есть примерно 3–4 тыс. токенов на каждую сессию.
- Описания сформулированы широко («Use when making any code change», «Use when
  implementing any logic»). Поэтому `git-workflow-and-versioning`,
  `test-driven-development` и `incremental-implementation` будут срабатывать
  почти на любой задаче с кодом.

### Пересечения с нашим `inventory/current.md`

- `code-review-and-quality` ↔ встроенный `code-review`; `code-simplification`
  ↔ `simplify`; `security-and-hardening` ↔ `security-review` и
  `anthropic-skills:security-review` (Odoo). Описания конкурируют за одни и те
  же запросы («review this diff», «simplify»).
- `/review` плагина конфликтует по имени со встроенной командой (автор сам
  советует `/agent-skills:review`).
- `spec-driven-development`, `planning-and-task-breakdown`,
  `incremental-implementation`, `test-driven-development` пересекаются с
  плагином `odoo19-mvp-build` (спека → код → тесты → ревью) и с цепочкой
  `tr-*` / `odoo-spec-writer`.
- `context-engineering` частично пересекается с `init`.
- Без аналога у нас: `doubt-driven-development`, `interview-me`,
  `source-driven-development`, `constraint-driven-development`,
  `idea-refine`, `observability-and-instrumentation`,
  `deprecation-and-migration`.

### Решения

- Плагин целиком не ставить: дубли со встроенными скиллами, широкие триггеры,
  3–4 тыс. токенов description на каждую сессию.
- Отобрали 6 скиллов для карточек (см. `items/`).

### Открытые вопросы

- Проверка «с ним / без него» не проводилась. Кандидаты для первой проверки:
  `doubt-driven-development` на реальном ТР/модуле Odoo и `interview-me` на
  размытом запросе клиента.
- Решить, нужен ли нам свой `source-driven` для Odoo 19 или хватит того, что
  уже есть в `tr-odoo-tech-design`.
