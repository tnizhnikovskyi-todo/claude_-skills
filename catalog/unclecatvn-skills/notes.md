# Журнал разбора: unclecatvn/agent-skills

## 2026-11-03, первичный разбор

**Что смотрели.** Клон `https://github.com/unclecatvn/agent-skills` в
scratchpad, коммит `82ebbae` (2026-10-16), плагин и npm-пакет `1.0.20`.
Ничего не запускали: ни `odoo_trace.py`, ни CLI, ни тесты, ни CI.

**Состав (по файлам, а не по README):**

| Часть | Объём | Что это |
|---|---|---|
| `skills/odoo-16.0` … `odoo-19.0` | по 22 файла; пак 19.0 — 19 справочников, ~180 КБ | Справочники по API фреймворка версии + `api-highlights.md` (что убрано/переименовано) |
| `skills/odoo-workflow` | `SKILL.md` 273 строки (~18,7 КБ), `odoo_trace.py` 1356 строк, `definition-of-done.md` 142 строки | Процедура «сначала трассировка исходников, потом код» |
| `agents/odoo-code-review.md`, `odoo-code-tracer.md` | 274 и 340 строк | Ревьюер с баллами и трассировщик, те же правила версии |
| `skills/odoo-commit` | 176 строк | Коммиты в стиле Odoo; **запрещает AI-атрибуцию** |
| `skills/dtg-base` | ~1000 строк | Справка по чужому модулю DTG Base (Odoo 18), нам не нужно |
| `rules/` | 2 файла | Общие правила с примерами на TypeScript, к Odoo не относятся |
| `bin/agent-skills.js` | CLI установки | Ходит в npm и GitHub API за версиями (только при запуске CLI) |
| `tests/` | `evals.json` (357 строк), фикстуры, `benchmark.md` | Свои A/B-прогоны и тесты хелпера |
| `website/`, `lib/video` | ~25 МБ | Лендинг и видео |

**Гипотеза «документация Odoo в виде скиллов»** подтвердилась частично.
Справочники есть (16–19), но главное в репозитории — метод: определить
версию по `odoo/release.py`, трассировать символы по реальным исходникам
хелпером и писать Context Brief, где у каждого утверждения есть `file:line`.

## Сверка фактов 19.0 с исходниками

Источник: `odoo/odoo` ветка `19.0`, коммит `e0b25b7` (2026-10-13),
sparse-клон `odoo/` + `addons/{base,mail,sale,account,web}/models`.

| # | Утверждение пака 19.0 | Где в исходниках | Итог |
|---|---|---|---|
| 1 | `_sql_constraints` игнорируется, warning `Model attribute '_sql_constraints' is no longer supported` | `odoo/orm/model_classes.py:162-163` | верно |
| 2 | `models.Constraint` / `Index` / `UniqueIndex` | `odoo/orm/table_objects.py:79,125,185` | верно |
| 3 | `read_group()` deprecated с 19.0 → `_read_group` / `formatted_read_group` | `odoo/orm/models.py:2754`, `addons/web/models/models.py:802` | верно |
| 4 | `self._cr/_uid/_context` deprecated с 19.0 | `odoo/orm/models.py:5932-5942` | верно |
| 5 | `@api.returns` убран из `odoo.api` | `odoo/api/__init__.py` (импорта нет), `private` есть (`decorators.py:328`) | верно |
| 6 | Без `_name` имя выводится из CamelCase с warning; строковый `_inherit` даёт `_name = _inherit`, список — нет | `odoo/orm/models.py:240-248` | верно |
| 7 | Новая БД без демо-данных, `--with-demo` | `odoo/tools/config.py:238` (`my_default=False`) | верно |
| 8 | `type='json'` → `type='jsonrpc'` | `odoo/http.py:812-818` (алиас с deprecation) | верно |
| 9 | У `res.groups` нет `category_id`, вместо него `privilege_id` → `res.groups.privilege` | `base/models/res_groups.py:36`; `res_groups_privilege.py:13` (там `category_id` есть, пример гайда корректен) | верно |
| 10 | `group_operator=` → `aggregator=` | `odoo/orm/fields.py:485-487` (ещё алиас с DeprecationWarning) | верно |
| 11 | Версия в `odoo/release.py` | `release.py:15` `(19, 0, 0, FINAL, 0, '')` | верно |

Устаревшие паттерны (`<tree>`, `attrs=`, `group_operator`,
`_sql_constraints`) в паке 19.0 встречаются только как «было → стало».

**Пробелы пака (как раз наша боль из `synthesis.md`):**
- нет удаления `res.partner.mobile` и `res.partner.title` в 19.0
  (`base/models/res_partner.py`: есть `phone`, нет `mobile`/`title`);
- нет переименования `res.users.groups_id` → `group_ids`
  (`res_users.py:257`); `group_ids` упомянут только у отчётов.

То есть пак покрывает API фреймворка, а не поля бизнес-моделей. Поля
ловит не текст, а хелпер `odoo_trace field MODEL FIELD`, если рядом есть
исходники 19.0.

## Безопасность (чтение кода)

- `odoo_trace.py`: только stdlib (`ast`, `configparser`, `csv`, `expat`,
  `glob`, `json`, `re`…), без `subprocess`, сети и записи файлов; открывает
  файлы на чтение; манифесты читает через `ast.literal_eval` (не `eval`).
  Код анализируемых модулей не импортирует.
- В плагине нет хуков и `.mcp.json`. Сеть есть только у CLI
  (`bin/agent-skills.js`: npm registry и GitHub releases для проверки версии).
- `definition-of-done.md` велит запускать `odoo-bin -i/-u` на scratch-БД и
  `odoo-bin db duplicate`, который рвёт соединения к исходной БД. Это
  осознанные действия разработчика, но в облаке у нас БД нет.
- `odoo-commit` прямо запрещает трейлеры `Co-Authored-By` и ссылки на
  сессию — конфликт с нашими правилами атрибуции.
- `.skillspector-baseline.yaml`: подавлено 95 находок сканера SkillSpector
  (65 × P2, 10 × RP1 и др.) как «accepted» без пояснений. Не проверяли,
  что это за правила; для нашего использования (только текст и хелпер)
  неважно.

## Стоимость контекста

- В плагине 8 скиллов. В каждой сессии висят описания всех паков 16–19
  (у 19 описание ~1,7 КБ) и `odoo-workflow` с триггером «Mandatory … ANY
  Odoo change». Поле `globs:` — формат Cursor, Claude Code его не
  использует.
- `odoo-workflow` `SKILL.md` ~18,7 КБ (~4,5 тыс. токенов) на каждую правку.
  По их же замеру скилл стоит ~2× токенов и ~1,7× вызовов инструментов.

## Их собственный A/B (не наш)

`tests/evals/odoo-workflow/benchmark.md`, тот же класс модели: 21/23 → 23/23
ожиданий в реалистичной постановке, выдуманное поведение Odoo 4 → 2 на 32
прогонах, сломанного кода 0 → 0; хелпер 34/34 ответа на вопросы
трассировки по 18 и 19. Честно пишут, что сильная модель с доступом к
исходникам и без скилла осторожна; прирост в обоснованности и полноте.

## Сравнение с нашим

- `odoo19-mvp-build:code-dev`: текста в этой сессии нет
  (`~/.claude/plugins/synced/*/` пуст, в `~/.claude/skills/synced` только
  `odoo-spec-writer` и `security-review`). Сравнение по существу не сделано —
  **открытый вопрос**.
- `boost:odoo-model-map`: см. `items/odoo-workflow.md`.
- `boost:source-check`: см. там же.

## Открытые вопросы к пользователю

1. Разрешить запуск `odoo_trace.py` (stdlib, только чтение) на sparse-клоне
   Odoo 19.0 в scratchpad? Хочу проверить `field res.partner mobile`,
   `field res.users groups_id`, `xmlid`, `method` — то, на чём модель
   ошибается.
2. Дать текст `odoo19-mvp-build:code-dev` (или включить плагин в сессии),
   чтобы сравнить с Context Brief.
3. A/B «source-check + справка 19.0» против «без» на трудных кейсах из
   `synthesis.md` — делать в сессии реализации.
