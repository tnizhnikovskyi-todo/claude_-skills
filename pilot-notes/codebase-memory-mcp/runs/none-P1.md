# none-P1

cost $0.186, turns 4, time 17.1s, in 6, cache_create 40502, cache_read 72821, out 1639

**Расширяют и наследуют `td.workshop.order`**

Модель определена в `addons/td_workshop/models/workshop_order.py:6` (`_name`, плюс `_inherit = ["mail.thread"]`). Расширений модели два:
- `addons/td_workshop_sale/models/workshop_order.py:6` — `_inherit = "td.workshop.order"`, модель.
- `addons/td_workshop_sale/views/workshop_order_views.xml:3-6` — вью `view_workshop_order_form_sale`, наследует `td_workshop.view_workshop_order_form`.

**Вью самой модели** (`addons/td_workshop/views/workshop_order_views.xml`)
- `:3` — list, `view_workshop_order_list`.
- `:20` — form, `view_workshop_order_form`.
- `:81` — search, `view_workshop_order_search`.
- `:98` — action `action_workshop_order`, на него ссылается меню `addons/td_workshop/views/menus.xml:4`.

**Ссылаются на модель**

| path:line | как |
|---|---|
| `addons/td_workshop_sale/models/sale_order.py:7` | `workshop_order_id` (Many2one в `sale.order`) |
| `addons/td_workshop_sale/views/sale_order_views.xml:9` | поле `workshop_order_id` в форме `sale.view_order_form` |
| `addons/td_workshop/models/workshop_order_line.py:8` | `order_id` (Many2one, cascade) |
| `addons/td_workshop/models/workshop_order.py:33` | `line_ids` (One2many на `td.workshop.order.line`) |
| `addons/td_workshop/models/close_wizard.py:8` | `order_id` (Many2one) |
| `addons/td_workshop/models/res_partner.py:11,19` | `search_count` и `res_model` в действии |
| `addons/td_workshop/views/res_partner_views.xml:9-11` | кнопка и счётчик в форме партнёра |
| `addons/td_workshop_portal/controllers/main.py:9` | `request.env[...].sudo().browse(order_id)` |
| `addons/td_workshop/data/ir_sequence.xml:5` | код последовательности (`workshop_order.py:55` вызывает `next_by_code`) |
| `addons/td_workshop/data/ir_cron.xml:5` | `model_td_workshop_order` |
| `addons/td_workshop/security/ir.model.access.csv:2-3` | права доступа (user и manager) |
| `addons/td_workshop/security/workshop_security.xml:10,16,23` | три record rules |
| `addons/td_workshop/tests/test_workshop_order.py:12,18` | тесты |

Искал grep по `td\.workshop\.order`, `workshop_order`, `workshop\.order`, `_inherit` и `inherit_id` в `addons/*.{py,xml,csv}`. Доступ к модели через динамические имена или через `memory/` и JS/QWeb-шаблоны таким поиском не проверялся. Файлы `td_workshop_portal` кроме `controllers/main.py` в выдачу не попали, их содержимое я не читал.

Не проверено / риск: содержимое `sudo()` в `td_workshop_portal/controllers/main.py:9` (есть ли комментарий «зачем») и тела файлов целиком не читал, только строки из grep. Каталоги вне `addons/` не искал.
