# Журнал разбора mart337i/odoo-skills

## 2026-11-03 — первичный разбор

### Что и откуда

- Клон `https://github.com/mart337i/odoo-skills` в scratchpad (вне репо).
  HEAD = `634b2db` (2026-10-01, «Update Odoo 20 migration guidance»), то есть
  совпадает с закреплённым коммитом; **HEAD не ушёл** (0 коммитов после).
- История: 10 коммитов, 2026-05-03 … 2026-10-01, один автор.
- **Лицензия.** Файла `LICENSE` нет. В `package.json` поле `"license": "MIT"`,
  но текста лицензии и копирайта нет. Считаем «лицензии нет»: ничего не
  копируем дословно, только идеи своими словами.
- Скилы `grill-me`, `grill-with-docs`, `improve-codebase-architecture`,
  `zoom-out` по именам и стилю похожи на набор mattpocock/skills; атрибуции
  в репозитории нет. Upstream не сверял (UNVERIFIED).
- Скрипты (`bin/odoo-skills.js`, `scripts/link-skills.sh`) прочитаны,
  **не запускались**. Хуков, сети, телеметрии нет.

### Что внутри (факт, а не README)

21 скилл, ~49.5 тыс. строк markdown:

- 4 справочника по версиям (`odoo-17.0` … `odoo-20.0`), в каждом `SKILL.md`
  с таблицей и 18 руководств в `references/` (Odoo 19: 8 603 строки вместе
  с ревью/тестами; сами 18 руководств 244–642 строки).
- Методы: `odoo` (маршрутизатор), `odoo-code-review`, `odoo-code-tracer`,
  `odoo-test-writer`, `odoo-web-security`, `odoo-web-testing`, `odoo-website`,
  `odoo-owl`, `odoo-report-design`, `odoo-report-migration`,
  `odoo-migration` (OCA `[MIG]`), `odoo-grill-me`, `odoo-idea-gates`.
- Общие: `grill-me`, `grill-with-docs`, `improve-codebase-architecture`,
  `zoom-out`.

Гипотеза «справочник Odoo 19 (18 руководств), ревью, тесты» —
**подтверждается**, но это лишь часть: справочников четыре версии, плюс
OWL, отчёты, веб-безопасность, OCA-миграции.

Наблюдение: руководства Odoo 20 — почти копия 19 (после замены «19»→«20»
отличие 4–168 строк на файл). Содержание «Odoo 20» не проверял, считаю
неподтверждённым. Руководства 19 и 18 сильно различаются (переписаны).

### Сверка фактов Odoo 19 с исходниками

Исходник: `odoo/odoo` ветка `19.0`, sparse-клон, коммит `e0b25b7`
(2026-11-03). Проверено 18 утверждений из `odoo-19.0/references/*` и
скиллов тестов.

**Верно (10):**

| Утверждение | Где в 19.0 |
|---|---|
| `models.Constraint(definition, message)` | `odoo/orm/table_objects.py:79–107` |
| `models.Index`, есть `UniqueIndex` | `odoo/orm/table_objects.py:125, 185` |
| `_sql_constraints` больше не поддерживается | `odoo/orm/model_classes.py:162–163` (warning, атрибут игнорируется) |
| `res.groups.privilege`, у групп `privilege_id` | `addons/base/models/res_groups_privilege.py:5`, `res_groups.py:36` |
| `category_id` теперь у привилегии, а не у группы | `res_groups_privilege.py:13` |
| `@api.private` (не вызывается по RPC) | `odoo/orm/decorators.py:328` |
| `from odoo.fields import Domain` | `odoo/fields/__init__.py:20` |
| `self.env.execute_query(SQL(...))` | `odoo/orm/environments.py:527` |
| `_read_group`, `search_fetch` | `odoo/orm/models.py:1867` |
| `Command.*` для x2many | — (стабильно с 15/16) |

**Ошибки (8):**

| Где | Что написано | Как в 19.0 | Последствие |
|---|---|---|---|
| `odoo-19-migration-guide.md` | хуки в манифесте `'pre_init_hook': 'my_module.pre_init_hook'` | загрузчик делает `getattr(py_module, имя)`: нужно просто имя функции (`odoo/modules/loading.py:182–185`) | `AttributeError` при установке |
| там же | `uninstall_hook` «после удаления модуля» | вызывается **до** `module_uninstall()` (`loading.py:541–547`) | неверная логика очистки |
| там же | «Ключевые изменения Odoo 19»: `<list>`, без `attrs`, `@api.ondelete`, `aggregator`, `SQL` | это изменения 14–18; настоящих изменений 19 (Constraint/Index, привилегии, `group_ids`, `jsonrpc`, Domain) в таблице нет | вводит в заблуждение при миграции |
| `odoo-19-controller-guide.md` (5 мест) | `type='json'` | с 19.0 это устаревший алиас `type='jsonrpc'` (`odoo/http.py:812–818`, warning) | работает, но с предупреждением; учит устаревшему |
| `odoo-19-reports-guide.md`, `actions-guide.md` | у `ir.actions.report` поле `groups_id` | `group_ids` (`ir_actions_report.py:183`; так же у `ir.actions.*`) | ошибка загрузки XML |
| `odoo-19-decorator-guide.md` | раздел `@api.returns` с примерами | декоратора в 19.0 нет (`odoo/orm/decorators.py`, нет и в `odoo/api`) | `AttributeError` при импорте модуля |
| `odoo-19-view-guide.md` | кнопки в `<header>` со `states="draft"` | с 17.0 `attrs`/`states` дают `ValidationError` (`ir_ui_view.py:495–497`) | вью не загрузится |
| `odoo-test-writer/ODOO-TESTING-EXAMPLES.md` | пользователь с `"groups_id": [(6, 0, …)]` | у `res.users` в 19.0 `group_ids` (`res_users.py:257`) | тест падает на создании пользователя |

Мелочь: `odoo-19.0/SKILL.md` ссылается на `odoo/models.py`, `odoo/fields.py`,
`odoo/api.py` как на исходники; в 19.0 это пакеты-обёртки, реализация в
`odoo/orm/*`.

Итог: ~55% верно. Новые вещи 19.0 (Constraint, привилегии, Domain,
`@api.private`) описаны правильно, но рядом лежат устаревшие примеры,
которые ломают установку. Ровно та слабость, которую показал наш пилот
(`synthesis.md` п.3): модель пишет удалённое в 19.0. Справочник её не
закрывает, местами закрепляет.

### Сравнение с нашими скиллами

- `odoo19-mvp-build:pr-review` и `:testing`: в контейнере
  `~/.claude/plugins/synced/*/` пуст, текстов нет. Доступ к `todo_timur`
  (`add_repo`) отклонён классификатором прав. Сравнение сделано по
  описаниям из `inventory/current.md` и прошлым карточкам; построчное
  сравнение — открытый вопрос.
- `boost:source-check`: метод «версия → источник → цитата, иначе
  UNVERIFIED». У них этого нет: есть только «если задан `$ODOO_SOURCE`,
  смотри исходник, а не память». Их справочник — как раз то, что
  source-check запрещает считать источником (вторичный текст без ссылок).
- `boost:odoo-model-map`: карта связей по строкам/XML. У них ближе всего
  `odoo-code-tracer` (трасса вызовов от точки входа). Это дополняет нас:
  model-map отвечает «кто связан», tracer — «что выполнится».

### Вопросы пользователю / решения

- (нет пока)

### Открытые вопросы

1. Построчно сравнить с `odoo19-mvp-build:pr-review` и `:testing`, когда
   будут тексты (нужен доступ к synced-плагинам или к `todo_timur`).
2. A/B не делали. Предложение: 3 кейса на Odoo 19 (JSON-контроллер,
   тест с пользователем в группе, хуки манифеста), три прогона:
   база / с `odoo-19.0` в контексте / с `boost:source-check`.
