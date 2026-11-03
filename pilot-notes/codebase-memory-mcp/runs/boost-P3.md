# boost-P3

cost $0.067, turns 6, time 14.1s, in 8, cache_create 9783, cache_read 147180, out 1316

**`_format_phone`** определён дважды, в разных моделях. Вызовов три:
- `td.workshop.order._format_phone` (`addons/td_workshop/models/workshop_order.py:66`) вызывают `create()` (`:59`) и `_onchange_partner_id` (`:64`).
- `sale.order._format_phone` (`addons/td_workshop_sale/models/sale_order.py:14`) вызывает только `_prepare_workshop_note` (`sale_order.py:11`). Её вызывает `addons/td_workshop_sale/models/workshop_order.py:32`.

**`_legacy_recompute`** (`workshop_order.py:96`) нигде не вызывается. Поиск по `_legacy_recompute`, `legacy`, `recompute` и `getattr(` нашёл только само определение. Строковых вызовов тоже нет: ни в XML, ни в cron, ни в тестах, ни через `getattr`. Это мёртвый код. Он к тому же расходится с рабочим `_compute_amount_total` (`:45-48`): тот учитывает `discount`, а legacy-версия нет. Если его кто-то вызовет, итог сменится на неверный.

**Дубль:** тело `_format_phone` в `td_workshop_sale` слово в слово повторяет код из `td_workshop`. Это не мёртвый код, но дубль. Убрать его можно, вынеся функцию в общее место, например в `res.partner` или в миксин.

Другой мёртвый код я не искал, только эти два метода. Ничего не менял.

Не проверено / риск: вызовы из внешних модулей, которых нет в репозитории, и из БД (серверные действия, `ir.cron` в данных БД). Искал по всему репозиторию текстом, а не по графу вызовов Odoo.
