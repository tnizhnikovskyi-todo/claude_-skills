# Атрибуция и происхождение правил

Скилл `odoo19-lint` написан в этом репозитории. Чужой код и тексты не
копировались: скрипт `scripts/odoo19_lint.py`, `SKILL.md` и
`references/rules.md` свои.

**Факты** (какое поле, метод или тег есть в 19.0) проверены самостоятельно
по исходникам `odoo/odoo`, ветка `19.0`, коммит
`e0b25b7032aacb5bf711a119c40a466888e2fc16` (sparse-клон, 2026-11-03; код
Odoo не запускался). Строки источника — в каждом правиле скрипта и в
`rules.md`. Правила, которые подтвердить не удалось, не включены (см. ниже).

## Откуда идеи

| Идея | Источник (`путь@SHA`) | Лицензия | Как взято |
|---|---|---|---|
| Линтер версионных ловушек как барьер после записи файла: правило → сообщение + исправление; правила `<tree>`, `attrs=`/`states=`, `type='json'`, `res.groups.category_id` | [infovpcs/odoo-agent-pro-kit](https://github.com/infovpcs/odoo-agent-pro-kit) `plugin/hooks/checks/odoo_lint.py@99515db` (разбор `catalog/odoo-agent-pro-kit/`) | Apache-2.0 | только идея; регэкспы и код свои (разбор через `ast`/expat вместо регэкспов по тексту) |
| `_inherit = [...]` списком без `_name` → новая модель в 19; правила `name_get`, `xpath //tree`, `tree_view_ref`, `group_operator`, `user_has_groups`, поля `res.groups` | [ChengyanOo/odoo-lens](https://github.com/ChengyanOo/odoo-lens) `@2482f92` (разбор `catalog/odoo-lens/`) | нет лицензии | только идея, своими словами; факт перепроверен по 19.0 |
| `self._cr/_uid/_context` устарели; удаление `res.partner.mobile/title` | разбор `catalog/unclecatvn-skills/notes.md` (сверка с 19.0) | — (наша заметка) | факт, перепроверен |
| `type='json'` → `jsonrpc`; `groups_id` → `group_ids` у `ir.actions.*`/`res.users`; `@api.returns` нет; хук манифеста по имени функции; `_sql_constraints` игнорируется | разбор `catalog/mart337i-odoo-skills/notes.md` (сверка с 19.0, `e0b25b7`) | — (наша заметка) | факт, перепроверен |
| `read_group` устарел в 19.0 (ошибка F2 в `code-dev`) | `catalog/dooservice-odoo-skills/`, `catalog/unclecatvn-skills/` (`roadmap.md` F2) | — | факт, перепроверен |
| `ir.cron numbercall/doall`, `view_mode tree`, `toggle_active`, `_notify_progress`, uom/товар/строка заказа | грейдеры `plugins/boost/evals/general/odoo19-api-traps`, `odoo19-sales-traps` (свои кейсы) | — | своё, перепроверено |

## Второй круг (2026-11-03)

Каждый факт перепроверен самостоятельно по `odoo/odoo` 19.0 (`e0b25b7`) и
18.0 (`f0ef96d`, sparse-клон), строки — в `rules.md`. Код источников не
копировался.

| Идея | Источник (`репозиторий@SHA`) | Лицензия | Как взято |
|---|---|---|---|
| `@api.model` + `create(self, vals)` — поломка в 19.0; `oe_chatter`; `odoo.osv.expression` → `Domain`; `_constraints` | [panusbodee-owen/odoo-dev-skill](https://github.com/panusbodee-owen/odoo-dev-skill) `@76e8b87` (`check_compat.py`; разбор `catalog/panus-odoo-dev-skill/`) | нет лицензии | только идея, своими словами |
| Ловушки 18→19, у источника помеченные как «с 20»: `fields.date/datetime`, `models.NewId`, `odoo.registry()`, `<group string/expand>` в поиске, `digits='Product Unit of Measure'`, `base.default_user`, `_login` classmethod, `default_get(fields_list)`, `tax_id`/`taxes_id`, удалённые аддоны; уровень «молча» (SILENT) | [tanim913/odoo-migrate-to-20](https://github.com/tanim913/odoo-migrate-to-20) `@a5507bf` (v1.9.0; разбор `catalog/odoo-migrate-to-20/`) | MIT | идея и список кандидатов; формулировки и код свои |
| Кандидаты `SavepointCase`, JS `useService("rpc"/"user")`, версия манифеста; ссылка на официальные кодмоды | [focuz-ai/odoo-spec-kit](https://github.com/focuz-ai/odoo-spec-kit) `@23df08b` (разбор `catalog/odoo-spec-kit/`) | MIT | идея (кит сам эти конструкции требует — использован как список антипримеров) |
| Автозамена: `odoo-bin upgrade_code --script …` | `odoo/odoo@19.0:odoo/upgrade_code/`, `odoo/cli/upgrade_code.py:168-174` | LGPL-3 | только ссылка в сообщении, код не взят |
| Барьер не должен срабатывать на справочниках, где запрещённое перечислено | урок darwin-skill (сообщение главной сессии, 2026-11-03) | — | идея: проверяются только файлы внутри модуля с `__manifest__.py` |

Проверено и уровень изменён против подсказки: `default_get(fields_list)`
как переопределение не ломается (позиционный вызов работает), поэтому
правило только на вызов с именем `fields_list=`.

## Проверено, но не включено

- `<group expand="…">` в поисковом вью: в первом круге не подтвердил по
  `search_view.rng`; во втором нашёл в `common.rng:295-313` (сравнение с
  18.0) — включено как `search-group-attrs`.
- Поля enterprise (например, возможное `mobile` в enterprise-аддонах) не
  проверялись: исходников enterprise нет. Подавление — комментарий
  `odoo19-lint: ignore`.

## Контроль ложных срабатываний

Скрипт прогнан на самом Odoo 19.0 (`addons/*/{models,views,data,security,
controllers,wizard}`, `odoo/addons/base`, 8962 файла; во втором круге 9884 файла вместе с JS `web`/`mail` и `odoo/tests`): 0 ERROR, 1 WARN
(настоящий вызов `read_group` в `addons/l10n_dk/models/account_account.py:22`).
