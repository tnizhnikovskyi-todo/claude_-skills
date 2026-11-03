# cloudflare/security-audit-skill (`security-audit`)

- **Тип:** скилл (один, с 12 файлами-компаньонами, JSON-схемой и 2 валидаторами на Node)
- **Источник:** https://github.com/cloudflare/security-audit-skill
- **Версия / коммит:** `c1c8a8c1471069fb0e188eeaff69b8e8db6564a8` (2026-09-14)
- **Лицензия:** MIT, © 2025-2026 Cloudflare, Inc. (сверено по `LICENSE`, с первого коммита; внешние PR — под ней же)
- **Дата разбора:** 2026-11-03
- **Вердикт:** скилл целиком — **отклонить** (10/18); методы — **адаптировать** точечно в `odoo19-mvp-build:security-review` (вопросы по классам атак 16/18; калибровка, повторный аудит, барьер покрытия)

## Что делает

Превращает агента в аудитора безопасности. По умолчанию режим «guidance»:
берёт нужные части методики без файлов. По явной просьбе «аудит / пентест /
полный разбор» запускает 6 фаз: разведка 4 агентами → охота волнами по
ledger покрытия с критиком покрытия после каждой волны → свежий
верификатор-опровергатель на каждого кандидата → `findings.json` по строгой
схеме + валидаторы → второй свежий верификатор на каждую финальную запись →
отчёты только из проверенных записей. Код цели исполняется только в
OS-песочнице; без неё — `needs_validation`.

## Какую слабость Claude закрывает

Ложные срабатывания и раздутая severity на полном аудите большого кода;
неполнота одного прохода (README: «один прогон — примерно половина того, что
нашли повторные»); отчёт без указания, что проверено. Для наших дифов `td.*`
две последние слабости уже закрыты Strix-версией `security-review`
(состояния закрытия, калибровка, таблица покрытия).

## Как устроен

| Компонент | Что | Карточка |
|---|---|---|
| `SKILL.md` (22 КБ) + `RECONNAISSANCE.md`, `HUNTING.md`, `VALIDATION-AND-REPORTING.md` | режимы, безопасность исполнения, профили и бюджет, 6 фаз, промпты агентов, анти-паттерны, якоря severity | [`items/workflow-verification.md`](items/workflow-verification.md) |
| `report-schema.json`, `validate-findings.cjs`, `validate-coverage-ledger.cjs` (+ тесты) | контракт `confirmed` / `needs_validation` / `rejected`, проверка формата и согласованности с ledger | [`items/findings-contract.md`](items/findings-contract.md) |
| `ATTACK-CLASSES.md` + 10 компаньонов по доменам | вопросы по классам атак; для Odoo важны Access control, Business logic, Feature abuse, Data isolation, CSRF-правило | [`items/attack-classes.md`](items/attack-classes.md) |

- **Права и сеть:** только текст. Хуков, MCP, `plugin.json`, телеметрии нет.
  Валидаторы — `fs`/`path`/`util`, только чтение входного файла; сети и
  `child_process` нет (`spawnSync` только в тестах). Не запускали.
- **Что ставится на машину:** по README — через `npx skills add` (сторонний CLI,
  код из `main`). Мы так не ставим.
- **Активность:** 14 коммитов 2026-06-18…09-14, 2 автора Cloudflare + 3 внешних PR;
  ★57 984, 111 открытых issues.

## Сравнение с нашим

С `odoo19-mvp-build:security-review` (Strix-версия, `proposals/odoo19-mvp-build/security-review/proposed/`;
сам приватный маркетплейс прочитать не дали — см. `notes.md`), встроенным
`/security-review`, `catalog/strix/`, `catalog/security-harness/`,
`catalog/repo-security-review/`.

| Аспект | cloudflare | наш `security-review` | Итог |
|---|---|---|---|
| Фазы | разведка → охота волнами → проверка кандидатов → JSON → проверка записей → отчёт | Step A `/security-review` + Step B 6 Odoo-измерений + опц. 3 критика | у них ширина на весь репо, у нас ворота на дифф; Odoo-знаний у них нет |
| Независимая проверка | опровергатель на каждого кандидата + второй на запись + третий при замене; может исполнять в песочнице | нет (`independent-check` отклонён, Δ=0) | в облаке исполнять нельзя → ожидаем Δ≈0; не переоткрывать |
| Полнота | критик покрытия по ledger после каждой волны | таблица покрытия заполняет тот же агент | **берём** как барьер-сверку диффа с таблицей, без агента |
| Состояния | confirmed / needs_validation (без severity) / rejected | confirmed / open_proof_gap / ruled_out | наше правило для ворот строже — оставить |
| Severity | likelihood × impact, overall ≤ impact; якоря critical…informational; различитель high/medium | Strix: VULN только если все 4 условия, «понижай, не удаляй» | **берём** различитель и «defense-in-depth / self-impact — не находка» |
| Формат | JSON по схеме + валидаторы | markdown с trace / counterevidence / gates | JSON не нужен (нет потребителя) |
| Повторные прогоны | fingerprint, перенос и перепроверка, `rejected` гасит только ту же претензию | «Critic round (iter N)» | **берём** таблицу повторного аудита по fingerprint |
| Фикс | наименьшее изменение в последней доверенной точке + регрессионный тест | 5 ворот фикса (Strix) | у нас сильнее; дописать фразу про «последнюю точку решения» |
| Стоимость | ~20–25 запусков агентов на модуль (оценка) | 1 агент, ~88k токенов | ×15–20 |

Против других разборов: Strix дал нам состояния и ворота (у Cloudflare похожее,
но слабее по фиксу); security-harness делит ширину по классам похожим образом,
но с опасной установкой; repo-security-review — та же идея «trace или
отклонённое подозрение» без лицензии. Новое у Cloudflare: критик покрытия,
повторный аудит по fingerprint, различитель high/medium, CSRF-правило,
вопросы Data isolation.

## Проверка

A/B не делали: полный процесс — десятки агентов, без разрешения не запускаем.
Если делать — дёшево и узко, на фикстурах `proposals/odoo19-mvp-build/tests/`:

| Задача | Без него | С ним |
|---|---|---|
| S1–S3 + 2 новые фикстуры (поле `company_id` в `write` от портала; `action_confirm` по RPC на черновике) — `security-review` текущий vs + `references/odoo-attack-questions.md` | не делали | не делали |
| То же + барьер «строки диффа ↔ таблица покрытия» | не делали | не делали |

## Оценка

Скилл как есть (для нашей работы):

| Критерий | Балл (0–3) | Комментарий |
|---|---|---|
| Прирост | 1 | На дифах `td.*` ожидаем ≈0 сверх нашего; Odoo-знаний нет |
| Частота | 1 | Полный аудит репо — редко |
| Надёжность | 2 | Подробно и с валидаторами, но длинный протокол, evals не опубликованы |
| Стоимость контекста | 0 | 5.5k токенов на любой вопрос о безопасности (широкий `description`), полный прогон ×15–20 |
| Безопасность | 3 | Код прочитан, только текст и read-only валидаторы, строгие правила исполнения |
| Поддержка | 3 | Cloudflare, активен, понятный источник |
| **Итого** | **10/18** | **Отклонить** как установку; методы — адаптировать |

## Что взять

| # | Исходный файл (`путь@SHA`) | Что берём | Куда у нас | Как | Лицензия |
|---|---|---|---|---|---|
| 1 | `skills/security-audit/ATTACK-CLASSES.md@c1c8a8c` (Access control, Business logic, Feature abuse), `DATA-ISOLATION-AND-LIFECYCLE.md@c1c8a8c` (Core discipline, Policy and query disagreement, Signed-reference overreach, Soft-delete) | 12 вопросов для Odoo 19 (таблица в `items/attack-classes.md`) | `odoo19-mvp-build:security-review` → `references/odoo-attack-questions.md`; задача **T5** | пересказ своими словами + Odoo-адаптация, атрибуция в `references/ATTRIBUTION.md` | MIT — разрешено |
| 2 | `skills/security-audit/WEB-PROTOCOL-AND-AUTH.md@c1c8a8c`, «Validation rules» п. 4 | правило CSRF-находки: ambient-учётка, изменяющий маршрут, кросс-сайтовая форма запроса, отсутствующая проверка; bearer-маршруты не подходят | то же, измерение 5 (после сверки Odoo-фактов, см. `UNVERIFIED`) | перевод/адаптация с атрибуцией | MIT |
| 3 | `skills/security-audit/SKILL.md@c1c8a8c`, «Separate priority from certainty» (якоря и различитель high/medium); «Anti-patterns» 2, 5; `README.md@c1c8a8c` «Design principles» | различитель «полностью снимает явный контроль или ослабляет»; «defense-in-depth и self-impact — не находка» | `security-review/references/closure-and-severity.md` (раздел рубрики) | перевод 2–3 фраз с атрибуцией + свои Odoo-примеры | MIT |
| 4 | `skills/security-audit/SKILL.md@c1c8a8c` «Coverage and prior runs»; `RECONNAISSANCE.md@c1c8a8c` «Prior-run input» | повторный аудит после правок: таблица fingerprint → закрыт / остался / новый; изменённый код → перепроверка | `security-review`, раздел вывода «Re-audit (iter N)» | идея, текст свой | MIT |
| 5 | `skills/security-audit/HUNTING.md@c1c8a8c` «Coverage-critic waves» | критик покрытия → **барьер без агента**: каждая строка диффа с `@http.route`/`sudo()`/`cr.execute`/`SQL(`/`Markup(`/новым `_name`/`ir.model.access.csv`/`ir.rule`/`groups=` обязана быть в таблице покрытия | `security-review`, правило вердикта («APPROVE без таблицы недействителен» → «…и без строк для этих мест»); позже grep-линтер | идея, текст свой | MIT |
| 6 | `skills/security-audit/VALIDATION-AND-REPORTING.md@c1c8a8c`, Phase 4, контракт `needs_validation` | план закрытия `open_proof_gap` в двух частях: локально (`HttpCase` + `with_user`) / на инстансе (→ `config-review`) | `security-review`, формат находки | идея, текст свой | MIT |

Не берём: процедуру переноса артефактов, бюджет агентов, двойную проверку
записей, JSON-схему и валидаторы, полный процесс фаз.

## Риски и заметки

- Широкий `description` («security questions, focused reviews…») пересекается
  со встроенным `/security-review` и нашим `security-review`; при установке
  грузил бы 5.5k токенов на любой вопрос о безопасности.
- Odoo-факты в п. 2 и части п. 1 не сверены с `odoo@19.0` — `UNVERIFIED`,
  сначала `source-check`.
- Приватный `security-review` в маркетплейсе не читали (доступ отклонён);
  сравнение — по `proposals/` и описанию установленного скилла.
- При переносе в маркетплейс атрибуция MIT: сохранить строку
  «Copyright (c) 2025-2026 Cloudflare, Inc.» и текст разрешения в
  `references/ATTRIBUTION.md` (если переводим фразы, п. 2–3).
