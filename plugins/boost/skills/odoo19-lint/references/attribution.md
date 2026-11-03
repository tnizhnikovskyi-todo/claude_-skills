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

## Проверено, но не включено

- `<group expand="…">` в поисковом вью (правило кита): по RNG
  `search_view.rng` 19.0 не подтвердил однозначно — не включено.
- Поля enterprise (например, возможное `mobile` в enterprise-аддонах) не
  проверялись: исходников enterprise нет. Подавление — комментарий
  `odoo19-lint: ignore`.

## Контроль ложных срабатываний

Скрипт прогнан на самом Odoo 19.0 (`addons/*/{models,views,data,security,
controllers,wizard}`, `odoo/addons/base`, 8962 файла): 0 ERROR, 1 WARN
(настоящий вызов `read_group` в `addons/l10n_dk/models/account_account.py:22`).
