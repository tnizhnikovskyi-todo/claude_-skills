---
name: odoo19-lint
description: >
  Барьер на ловушки Odoo 19: проверка файлов модуля (Python, XML вью/данных/прав,
  CSV, __manifest__.py) на API и поля, удалённые или переименованные в 18–19
  (<tree>, attrs=/states=, view_mode tree, _sql_constraints, res.partner.mobile/
  title, res.groups.users/category_id, groups_id, _inherit списком без _name,
  ir.cron numbercall, name_get, read_group, self._context, type='json',
  uom category_id, product type 'product', sale.order.line.product_uom/tax_id,
  @api.model create, oe_chatter, <group expand> в поиске, удалённые аддоны).
  Вызывай ПОСЛЕ того, как написал или изменил файлы модуля Odoo 19 (модели,
  вью, группы, крон, данные, контроллер) и ДО ответа «готово»/ревью/коммита;
  или по просьбе «проверь модуль на ловушки 19», «odoo19-lint», «установится
  ли в 19». Не вызывай для других версий Odoo (≤18), для вопросов без кода,
  для не-Odoo проектов.
---

# odoo19-lint

Модель пишет Odoo 19 по памяти о 16–18: код выглядит правильно, но модуль
не установится или молча потеряет ограничение. Этот скилл — проверка
перед «готово», а не справочник: прогони, исправь, перепроверь.

## 1. Когда

- Ты только что записал/изменил файлы модуля Odoo 19 → проверь **все
  изменённые** файлы до финального ответа.
- Просят ревью/проверку модуля 19 → проверь модуль целиком.
- Версию бери из `__manifest__.py` (`'version': '19.0.…'`) или слов
  пользователя. Если модуль не 19 — скажи и не применяй правила.

## 2. Проверка

**Есть Bash и python3** — запусти скрипт из папки этого скилла (stdlib,
анализируемый код не импортирует и не исполняет):

```bash
python3 -I <папка скилла>/scripts/odoo19_lint.py <модуль или файлы> [--json]
```

Выход 1 — есть ERROR. Каждая находка: `уровень [правило] файл:строка`,
«что», «исправить», «источник» (`odoo/odoo@19.0:путь:строки`).

**Bash нет** (или скрипт недоступен) — проверь сам: Read каждого
изменённого файла и сверка с таблицей ниже; полные правила с примерами и
источниками — `references/rules.md`. Grep-рецепты там же.

Проверяй только файлы модуля (каталог с `__manifest__.py`): справочники,
`*.md`, скрипты и `references/` перечисляют запрещённое как пример —
это не находки. Скрипт сам пропускает всё вне модулей (`--all-files`
снимает ограничение).

Часть правил можно исправить официальным кодмодом Odoo 19:
`odoo-bin upgrade_code --script tree-to-list|sql-constraint|route-jsonrpc|deprecated-properties --dry-run`
(скрипт печатает строку «автозамена»). Прогон кодмода — только с
согласия пользователя: он переписывает файлы.

## 3. Ловушки (кратко)

| Где | Нельзя в 19 | Нужно |
|---|---|---|
| вью | `<tree>`, xpath `//tree`, `…/tree` | `<list>`, `//list` |
| вью | `attrs="{…}"`, `states="draft"`, `<attribute name="attrs">` | `invisible="state != 'draft'"`, `readonly="…"`, `required="…"` |
| действие | `view_mode` `tree,form`; `(False, 'tree')`; `tree_view_ref` | `list,form`; `(False, 'list')`; `list_view_ref` |
| модель | `_sql_constraints = [...]` (игнорируется!) | `_x_uniq = models.Constraint('UNIQUE(x)', 'msg')` |
| модель | `_inherit = ['x']` без `_name` (это НОВАЯ модель из имени класса) | `_inherit = 'x'` или `_name = 'x'` + список |
| res.partner | `mobile`, `title` (в related, depends, вью, коде) | `phone`; обращения нет — своё поле или без него |
| res.groups | `users`, `category_id` | `user_ids`, `privilege_id` → запись `res.groups.privilege` с `category_id` |
| res.users, ir.ui.menu, ir.actions.*, ir.ui.view | `groups_id` | `group_ids` |
| ir.cron | `numbercall`, `doall` | убрать; продолжение пачками — `_commit_progress` |
| ORM | `name_get` | `_compute_display_name`, `display_name` |
| ORM (warn) | `read_group()`, `toggle_active()`, `self._context/_cr/_uid`, `_notify_progress`, `group_operator=` | `_read_group`/`formatted_read_group`, `action_archive/unarchive`, `self.env.context/cr/uid`, `_commit_progress`, `aggregator=` |
| ORM | `@api.returns`, `user_has_groups()` | убрать; `self.env.user.has_group()` |
| контроллер (warn) | `@route(type='json')` | `type='jsonrpc'` |
| uom.uom | `category_id`, `uom_type`, `factor_inv` | `relative_factor` + `relative_uom_id` |
| товар | `detailed_type`, `type='product'` | `type='consu'` + `is_storable=True` |
| sale/purchase.order.line | `product_uom` | `product_uom_id` (у `stock.move` — `product_uom`) |
| манифест | `'pre_init_hook': 'mod.hooks.f'`; `'version': '18.0.1.0.0'` (молча `installable=False`); `depends` на `web_editor`, `hr_contract`, `membership`, `website_jitsi`… | `'f'`; `'19.0.x.y.z'`; `html_editor`, `hr` |
| ORM | `@api.model` + `def create(self, vals)` (в 19 получит СПИСОК) | `@api.model_create_multi`, `vals_list` |
| ORM | `_constraints = [...]` (игнорируется) | `@api.constrains` |
| импорт | `fields.date/datetime`, `models.NewId`, `odoo.registry()`, `SavepointCase`, `odoo.osv.expression` (warn) | `fields.Date`, `odoo.api.NewId`, `Registry(db)`/`env.registry`, `TransactionCase`, `Domain` |
| поиск | `<group expand="0" string="…">` в `<search>` | `<group>` без атрибутов |
| форма | `<div class="oe_chatter">` (чаттер молча пропадает) | `<chatter/>` |
| точность | `digits='Product Unit of Measure'` (молча 2 знака) | `digits='Product Unit'` |
| права | `base.default_user`; `_login(cls, db, …)` classmethod | `base.default_user_group`; `def _login(self, credential, user_agent_env)` |
| строки заказа | `sale.order.line.tax_id`, `purchase.order.line.taxes_id` | `tax_ids` |
| JS | `useService("rpc")`, `useService("user")` | `import { rpc }` / `import { user }` из `@web/core/...` |

## 4. Как читать и что делать

1. **ERROR** — модуль не установится, упадёт или молча потеряет поведение.
   Исправь до ответа. **WARN** — устаревшее: исправь в своём новом коде,
   в чужом — перечисли.
2. Находка скрипта — заготовка. Перепроверь строку Read'ом: если модуль
   **сам** добавляет поле (например, своё `mobile` в `res.partner`),
   скрипт это видит только в переданных путях; поле из другого аддона —
   ложное срабатывание, подави комментарием `odoo19-lint: ignore` и
   скажи почему.
3. После правки — **повторный прогон** (или повторная сверка). Цель:
   0 ERROR в изменённых файлах.
4. «Нет находок» ≠ «установится»: скрипт не видит ядро, enterprise,
   JS/OWL, динамический код. Не пиши «проверено, установится» — пиши
   «odoo19-lint: 0 ERROR».

## 5. Ответ

Коротко, после основной работы:

```
odoo19-lint: <N> ERROR, <M> WARN → исправлено: <что> (правило, файл:строка);
осталось: <WARN в чужом коде / подавлено и почему>.
```

Если правило было применено по таблице без скрипта — так и напиши
(«сверено по references/rules.md, скрипт не запускался»).

Происхождение правил и источников: `references/attribution.md`.
