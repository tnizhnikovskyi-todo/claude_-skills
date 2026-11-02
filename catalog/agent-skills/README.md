# addyosmani/agent-skills

- **Тип:** плагин Claude Code (24 скилла, 9 команд, 4 агента-персоны,
  опциональные хуки); также ставится в Codex, Gemini CLI, Cursor и др.
- **Источник:** https://github.com/addyosmani/agent-skills
- **Версия / коммит:** 0.6.15 / `301b02b12bff98e4688e6984af6556802322bbde` (2026-11-01)
- **Дата разбора:** 2026-11-02
- **Вердикт:** **адаптировать выборочно.** Плагин целиком не ставить.
  Взять `interview-me`. Адаптировать `doubt-driven-development`,
  `source-driven-development` (под Odoo 19) и «пол» из
  `constraint-driven-development`. Остальное отклонить или взять отдельные
  приёмы.

## Что делает

Набор методичек «как работает senior-инженер» на весь цикл разработки:
DEFINE → PLAN → BUILD → VERIFY → REVIEW → SHIP. Каждый скилл представляет
собой один `SKILL.md` (200–400 строк) с процессом, таблицей «типичных
отговорок», красными флагами и чек-листом проверки. Команды `/spec`, `/plan`,
`/build`, `/test`, `/review`, `/code-simplify`, `/constraints`, `/webperf`,
`/ship` вызывают нужные скиллы. Свой эвал-контур: проверка структуры,
проверка триггеров по TF-IDF и поведенческие прогоны через headless `claude`.

## Какую слабость Claude закрывает

В основном **метод** (п. 2 из `README.md` нашего репозитория): дисциплина,
которую Claude соблюдает непоследовательно. Это проверка своих решений
свежим взглядом, выяснение настоящих требований, сверка с документацией,
запрет тихо опускать планку качества. Новых знаний и инструментов почти не
даёт (исключение: `browser-testing-with-devtools` через сторонний MCP).

## Как устроен

- `.claude-plugin/plugin.json` подключает только `skills/` и `commands/`.
  Хуков по умолчанию нет.
- Скрипты: `quality-gate.mjs` (читает JSON semgrep/axe), `idea-refine.sh`
  (`mkdir docs/ideas`). Оба безопасны.
- Опциональные хуки: `session-start.sh` (вставляет мета-скилл), `sdd-cache`
  (кэш WebFetch через `curl -I`), `simplify-ignore` (переписывает файлы на
  диске при Read). Последние два **не ставить**, подробности в `notes.md`.
- Сеть: только в инструкциях (WebFetch документации, `npx` в примерах CI).

## Перечень скиллов

Оценка: ★ взять, ◐ адаптировать или взять приём, ✕ отклонить. «Дубль» значит,
что у нас уже есть аналог.

| Скилл | Что делает | Слабость Claude | КБ | Вердикт |
|---|---|---|---|---|
| [`doubt-driven-development`](items/doubt-driven-development.md) | Враждебная проверка решения субагентом со свежим контекстом, без CLAIM | Самоподтверждение | 16.7 | ◐ лучшая находка |
| [`interview-me`](items/interview-me.md) | Интервью по одному вопросу с догадкой, до ~95% уверенности, явное «да» | Молча додумывает требования | 15.1 | ★ |
| [`source-driven-development`](items/source-driven-development.md) | Версии → официальная документация → код → цитаты | Устаревшие API по памяти | 10.1 | ◐ под Odoo 19 |
| [`constraint-driven-development`](items/constraint-driven-development.md) | `CONSTRAINTS.md`, «пол» качества, храповики | Ослабляет проверки ради зелёного CI | 22.2 | ◐ только «пол» |
| [`code-review-and-quality`](items/code-review-and-quality.md) | Ревью по 5 осям, метки серьёзности | — | 21.3 | ✕ дубль `code-review`; 4 приёма взять |
| `code-simplification` | Упрощение без смены поведения, «забор Честертона» | — | 13.7 | ✕ дубль `simplify` |
| `security-and-hardening` | OWASP, секреты, supply chain, GDPR | — | 17.6 | ✕ дубль `security-review` |
| [`debugging-and-error-recovery`](items/debugging-and-error-recovery.md) | Stop-the-line, reproduce → localize → reduce → fix → guard | Чинит симптом | 10.9 | ◐ 3 строки в CLAUDE.md |
| `test-driven-development` | Red-green-refactor, Prove-It для багов | Фикс без доказательства | 16.8 | ◐ Prove-It в CLAUDE.md |
| `idea-refine` | Расходящееся → сходящееся мышление по идее, `docs/ideas/` | Хватается за первую идею | 9.4 | ✕ редко нужен, частично покрыт `interview-me` |
| `spec-driven-development` | PRD/спека до кода | — | 13.1 | ✕ дубль `odoo-spec-writer` / `tr-*` |
| `planning-and-task-breakdown` | Разбивка спеки на задачи | — | 10.6 | ✕ дубль `odoo19-mvp-build` |
| `incremental-implementation` | Тонкие проверяемые срезы, feature flags | Пишет много за раз | 9.6 | ✕ слишком широкий триггер |
| `api-and-interface-design` | Стабильные API, контракты, границы | — | 14.9 | ✕ для нас редко |
| `frontend-ui-engineering` | Доступный адаптивный UI «не как от ИИ» | — | 12.0 | ✕ пересекается с `artifact-design` |
| `browser-testing-with-devtools` | Проверка в браузере через MCP `chrome-devtools` | Не видит рантайм | 14.6 | ✕ сторонний npx MCP; у нас есть Playwright и `run` |
| `performance-optimization` | Профилирование, CWV, N+1 | — | 16.8 | ✕ редко |
| `observability-and-instrumentation` | Логи, метрики, трейсинг, алерты | — | 13.9 | ✕ редко (возможно, для go-live) |
| `ci-cd-and-automation` | CI/CD пайплайны, quality gates | — | 11.5 | ✕ редко, примеры под Vercel/npm |
| `deprecation-and-migration` | Вывод из эксплуатации, expand/contract миграции БД | — | 12.8 | ✕ редко; идея expand/contract полезна для миграций Odoo |
| `documentation-and-adrs` | ADR и документация решений | — | 11.0 | ✕ редко |
| `git-workflow-and-versioning` | Атомарные коммиты, сообщения, semver, changelog | — | 14.4 | ✕ слишком широкий триггер («any code change») |
| `shipping-and-launch` | Чек-лист запуска, rollback, staged rollout | — | 11.5 | ✕ дубль `odoo19-implementation` |
| `context-engineering` | Иерархия контекста, rules-файлы, бюджет контекста | — | 15.5 | ✕ частично `init`; полезно почитать человеку |
| `using-agent-skills` | Мета-скилл маршрутизации | — | 10.4 | ✕ в Claude Code не нужен (сам автор так пишет) |

Агенты `code-reviewer`, `security-auditor`, `test-engineer`,
`web-performance-auditor` представляют собой персоны-промпты на 50–100 строк.
Встроенные возможности их перекрывают.

## Проверка

| Задача | Без него | С ним |
|---|---|---|
| Не проводилась | — | Предложено: `doubt-driven` на ТР/модуле Odoo; `interview-me` на размытом запросе клиента |

## Оценка (плагин целиком)

| Критерий | Балл | Комментарий |
|---|---|---|
| Прирост | 2 | 3–4 сильных метода, остальное Claude знает и так |
| Частота | 3 | Разработка и требования: каждую неделю |
| Надёжность | 1 | Широкие триггеры, конфликты со встроенными `code-review`/`simplify`/`security-review` и с `/review` |
| Стоимость контекста | 1 | ~3–4 тыс. токенов description в каждой сессии; 10–22 КБ на срабатывание |
| Безопасность | 3 | Скиллы являются чистым markdown, скрипты прочитаны; рискованные хуки выключены по умолчанию |
| Поддержка | 3 | Очень активно (198 коммитов в октябре 2026), известный автор, MIT, свои эвалы |
| **Итого** | **13/18** | |

## Риски и заметки

- При установке одного скилла через `npx skills add` общие `references/`
  не копируются, и ссылки на чек-листы ломаются (issue #361 у автора).
- Если адаптировать, переписывать сжато (до ~80–120 строк): таблицы
  «отговорок» и «красных флагов» занимают треть объёма.
