# boost-P1

cost $0.095, turns 7, time 18.9s, in 8, cache_create 14482, cache_read 151533, out 2214

**Карта.** Модули: `td_workshop` → `td_workshop_sale`, `td_workshop_portal`. Модель определена в `td_workshop`.

**Расширяют и наследуют `td.workshop.order`**
- Определение модели (`_name`, миксин `mail.thread`): `addons/td_workshop/models/workshop_order.py:6` и `:8`.
- Расширение модели (`_inherit = "td.workshop.order"`, без нового `_name`): `addons/td_workshop_sale/models/workshop_order.py:6`. Оно добавляет создание `sale.order` и действие с `res_model: sale.order`, строки 30 и 37.
- Расширение формы через `inherit_id` на `td_workshop.view_workshop_order_form`: `addons/td_workshop_sale/views/workshop_order_views.xml:3-6`.
- Модели с `_inherits` на неё не нашёл.

**Вью модели (все в `addons/td_workshop/views/workshop_order_views.xml`)**
- list, `view_workshop_order_list`: строка 3.
- form, `view_workshop_order_form`: строка 20.
- search, `view_workshop_order_search`: строка 81.
- action `action_workshop_order` (`res_model`): строка 98. Меню на него: `addons/td_workshop/views/menus.xml:4`.

**Кто на неё ссылается**
- `addons/td_workshop/models/workshop_order_line.py:8`: `order_id` (Many2one, cascade). Обратная связь `line_ids` (One2many) в `workshop_order.py:33`.
- `addons/td_workshop/models/close_wizard.py:8`: `order_id` (Many2one, required).
- `addons/td_workshop_sale/models/sale_order.py:7`: `workshop_order_id` (Many2one) в `sale.order`. Показано во вью `addons/td_workshop_sale/views/sale_order_views.xml:9`.
- `addons/td_workshop/models/res_partner.py:11` и `:19`: `search_count` и `res_model` для кнопки на партнёре. Кнопка во вью `addons/td_workshop/views/res_partner_views.xml:9-11`.
- `addons/td_workshop_portal/controllers/main.py:9`: `request.env["td.workshop.order"].sudo().browse(order_id)`. Комментария «зачем sudo» рядом нет, это против правила из CLAUDE.md. Я его не искал отдельно, только увидел в выдаче.
- `addons/td_workshop/data/ir_sequence.xml:5`: код последовательности. Использует `workshop_order.py:55`.
- `addons/td_workshop/data/ir_cron.xml:5`: cron `cron_workshop_notify_overdue` на `model_td_workshop_order`.
- `addons/td_workshop/tests/test_workshop_order.py:12` и `:18`: тесты.

**Права и правила**
- `addons/td_workshop/security/ir.model.access.csv:2-3`: у `base.group_user` права 1,1,1,0, у `group_workshop_manager` права 1,1,1,1.
- `addons/td_workshop/security/workshop_security.xml:8`, `:14`, `:21`: три `ir.rule`: `rule_workshop_order_company`, `rule_workshop_order_technician`, `rule_workshop_order_manager`. Домены и группы я не читал.

**Где не искал:**
- Скрипт `odoo_map.py` не запускал: Bash запросил подтверждение. Использовал Grep по `*.py`, `*.xml`, `*.csv`, `*.js`, `*.json` в `addons/`, затем читал только строки из выдачи.
- Ядро Odoo 19 и enterprise, другие репозитории.
- Данные БД: фильтры, серверные действия, автоматизации.
- QWeb-шаблоны портала и динамические имена (`env[var]`, `getattr`) отдельно не проверял.
- Другие `inherit_id` на вью заказа, кроме найденного, искал только по строкам `inherit_id` в `*.xml` внутри `addons/`.

Не проверено / риск: скрипт не запускался, карта построена только Grep'ом. Содержимое `ir.rule` и `sudo()` в портале не читал.
