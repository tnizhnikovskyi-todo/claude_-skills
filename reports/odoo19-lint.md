# Отчёт: T2 `odoo19-lint`

Ветка `build/odoo19-lint`. Задача T2 из `roadmap.md` («Третий проход»):
барьер на главную слабость модели — факты Odoo 19 (`synthesis.md` п. 3).
Основа: идеи из `catalog/odoo-agent-pro-kit/` (линтер `checks/odoo_lint.py`,
Apache-2.0 — только идея), `catalog/odoo-lens/` (без лицензии — только
идеи), сверенные факты из `catalog/unclecatvn-skills/`,
`catalog/mart337i-odoo-skills/`, `catalog/dooservice-odoo-skills/`, и
F2–F5. Код и тексты свои.

## Что сделано и где

| Путь | Что |
|---|---|
| `plugins/boost/skills/odoo19-lint/SKILL.md` (~100 строк) | Триггер: после записи/правки файлов модуля Odoo 19 и до «готово»/ревью/коммита, либо «проверь на ловушки 19». Не для Odoo ≤ 18, вопросов без кода и не-Odoo. Шаги: скрипт (если есть Bash) или сверка по таблице/`references/rules.md` (если нет); как читать ERROR/WARN; повторная проверка; формат строки итога; «0 находок ≠ установится» |
| `plugins/boost/skills/odoo19-lint/scripts/odoo19_lint.py` (~600 строк, stdlib) | 23 правила. Python — `ast` (код не импортируется), XML — `expat` со строками, CSV — `csv` (модель по имени файла), манифест — `ast.literal_eval`. Учитывает поля, которые модуль сам добавляет (`mobile` в своём `res.partner` — не ошибка), любые Many2one на `res.partner` (`driver_id.mobile`), подавление `odoo19-lint: ignore`. `--json`, `--rules`; выход 1 при ERROR |
| `plugins/boost/skills/odoo19-lint/references/rules.md` | Все правила для режима без Bash: что, почему, как исправить, источник `odoo/odoo@19.0:путь:строки`, Grep-рецепт |
| `plugins/boost/skills/odoo19-lint/references/attribution.md` | Откуда идеи, лицензии, что проверено и не включено, контроль ложных срабатываний |
| `plugins/boost/evals/odoo19-lint/test_odoo19_lint.py` | 11 unittest: позитив на каждое правило (`tests/bad/`), ноль находок на правильном коде 19 (`tests/good/`), подавление, поле модуля, пилот (K9), ключ eval-фикстуры |
| `plugins/boost/evals/odoo19-lint/tests/{bad,good}/td_lint/` | Один и тот же модуль: с ловушками и правильно для 19 |
| `plugins/boost/evals/odoo19-lint/_fixture/addons/td_rental/` | Модуль для кейса ревью: 7 ловушек ERROR + 2 WARN среди правильного кода 19 |
| `plugins/boost/evals/odoo19-lint/{review-module,write-module,odoo16-negative}/` | 3 eval-кейса |

```bash
python3 -I -m unittest discover -s plugins/boost/evals/odoo19-lint -p 'test_*.py'   # 11 OK
python3 -I plugins/boost/skills/odoo19-lint/scripts/odoo19_lint.py <модуль>
claude plugin validate plugins/boost                                               # passed
```

## Правила и источники

Все строки сверены по `odoo/odoo` ветки `19.0`, коммит `e0b25b7`
(sparse-клон в scratchpad, код Odoo не запускался).

| Правило | Уровень | Что ловит | Источник `odoo/odoo@19.0:` |
|---|---|---|---|
| `view-tree` | ERROR | `<tree>`, xpath `//tree`, `…/tree` | `odoo/addons/base/models/ir_ui_view.py:149-156`, `:610-617` |
| `view-mode-tree` | ERROR | `view_mode` с `tree`, `(False, 'tree')` | `odoo/addons/base/models/ir_actions.py:318`, `:401-408`; `ir_ui_view.py:3054-3058` |
| `tree-view-ref` | WARN | контекст `tree_view_ref` | `ir_ui_view.py:3024-3026` |
| `view-attrs-states` | ERROR | `attrs=`, `states=`, `<attribute name="attrs">` | `ir_ui_view.py:495-499` |
| `route-type-json` | WARN | `@route(type='json')` | `odoo/http.py:812-818` |
| `sql-constraints` | ERROR | `_sql_constraints` (игнорируется) | `odoo/orm/model_classes.py:159-164` |
| `partner-mobile-title` | ERROR | `res.partner.mobile/title` в related, depends, коде, вью, xpath | `odoo/addons/base/models/res_partner.py:184-313` (+ ни один `addons/*/models/*.py` не добавляет) |
| `groups-fields` | ERROR | `res.groups.users/category_id`, `groups_id` у `res.users`, `ir.ui.menu`, `ir.actions.*`, `ir.ui.view` (XML, Python, CSV) | `res_groups.py:17,36`; `res_groups_privilege.py:13`; `res_users.py:257`; `ir_ui_menu.py:29`; `ir_actions.py:329,661`; `ir_actions_report.py:183`; `ir_ui_view.py:175` |
| `inherit-list-no-name` / `-implicit-name` | ERROR / WARN | `_inherit = [...]` без `_name`: новая модель (или совпадение имени класса) | `odoo/orm/models.py:241-249` |
| `cron-numbercall` | ERROR | `ir.cron` `numbercall`, `doall` | `ir_cron.py:99-122` |
| `name-get` | ERROR | `def name_get`, `.name_get()` | `odoo/orm/models.py:1438`; `name_get` в `odoo/` нет |
| `read-group` | WARN | `read_group()` | `odoo/orm/models.py:2754-2755` |
| `private-env` | WARN | `self._context/_cr/_uid` | `odoo/orm/models.py:5930-5943` |
| `toggle-active` | WARN | `toggle_active()` | `odoo/orm/models.py:5807-5813` |
| `notify-progress` | WARN | `_notify_progress()` | `ir_cron.py:823-824`, `:846` |
| `api-returns` | ERROR | `@api.returns` | `odoo/api/__init__.py:5-17` |
| `user-has-groups` | ERROR | `user_has_groups()` | `res_users.py:1034,1066` |
| `group-operator` | WARN | `group_operator=` | `odoo/orm/fields.py:485-487` |
| `product-type` | ERROR | `detailed_type`, `type='product'` | `addons/product/models/product_template.py:58-65`; `addons/stock/models/product.py:834` |
| `uom-fields` | ERROR | `uom.uom` `category_id/uom_type/factor_inv` | `addons/uom/models/uom_uom.py:34-44` |
| `line-product-uom` | ERROR | `product_uom` у `sale/purchase.order.line` (не `stock.move`) | `addons/sale/models/sale_order_line.py:132`; `addons/purchase/models/purchase_order_line.py:43`; `addons/stock/models/stock_move.py:67` |
| `manifest-hook-path` | ERROR | хук манифеста путём с точкой | `odoo/modules/loading.py:182-185` |

Не включено: `<group expand>` в поиске (правило кита) — по RNG 19.0 не
подтвердил однозначно.

## Проверка скрипта

- **unittest:** 11 тестов, все проходят. На `bad/` найдено ровно ожидаемое
  (по позитиву на каждое правило, тест сверяет множество целиком, лишних
  нет), на `good/` — 0 находок.
- **Ложные срабатывания на самом Odoo 19.0:** `addons/*/{models,views,data,
  security,controllers,wizard}`, `__manifest__.py`, `odoo/addons/base` —
  8962 файла: **0 ERROR, 1 WARN** (настоящий `self.read_group` в
  `addons/l10n_dk/models/account_account.py:22`). По ходу так нашлись и
  убраны два ложных срабатывания: `move.product_uom` (у `stock.move` поле
  осталось) и ключ `'product_uom'` в vals для `stock.move`.
- **Пилот `pilot/addons` (K9):** ровно 1 находка —
  `partner-mobile-title td_workshop/models/workshop_order.py:17`
  (`related="partner_id.mobile"`), это K9 из `pilot-notes/KEYS.md`. Ловушки
  «не ошибки» из ключа (`models.Constraint`, `<list>`, `invisible=`,
  `<chatter/>`) не задеты. Остальные K* — не версионные, вне задачи линтера.

## A/B

_(заполняется после прогонов)_
