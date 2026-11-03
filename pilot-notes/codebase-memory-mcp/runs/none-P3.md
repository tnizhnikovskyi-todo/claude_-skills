# none-P3

cost $0.067, turns 6, time 16.0s, in 8, cache_create 9105, cache_read 138584, out 1603

**`_format_phone`** — два независимых определения, оба вызываются:
- `td.workshop.order._format_phone`, `addons/td_workshop/models/workshop_order.py:66`. Вызовы: `workshop_order.py:59` (в `create`) и `:64` (в `_onchange_partner_id`).
- `sale.order._format_phone`, `addons/td_workshop_sale/models/sale_order.py:14`. Вызов: `sale_order.py:11` (в `_prepare_workshop_note`). Её вызывает `addons/td_workshop_sale/models/workshop_order.py:32`.

**`_legacy_recompute`** (`workshop_order.py:96`): вызовов не нашёл. Совпадение по имени только на самом определении. Я проверил это так:
- Grep по имени по всему репозиторию.
- Grep по `getattr`, `legacy`, `recompute`, `.call(`, `ir.cron`.
- Чтение `data/ir_cron.xml`: cron вызывает только `_cron_notify_overdue`.

В XML-вьюхах и в `td_workshop_portal` я отдельно не смотрел. Вызов оттуда был бы виден в grep по имени, так что почти наверняка его нет. Это кандидат в мёртвый код.

Есть и расхождение в логике. `_legacy_recompute` считает `quantity * price_unit` без скидки. `_compute_amount_total` (`:45-48`) считает `subtotal` со скидкой `discount`. Если метод когда-нибудь вызовут, итог будет другим. Поэтому удалять его стоит только после проверки на вызовы из сторонних модулей или из shell. Удаление я не делал.

**Дубль, не мёртвый код:** тело `_format_phone` одинаковое в двух модулях. `td_workshop_sale` не наследует `td.workshop.order`, поэтому модели разные и метод скопирован. Можно вынести его в общий хелпер. Сейчас правка в одном месте не попадёт во второе.

Других мёртвых методов в просмотренных фрагментах нет. Файл `workshop_order.py` я читал только со строки 45, начало и конец после строки 114 не смотрел.

Не проверено / риск: вызовы из XML-вьюх и `td_workshop_portal`, начало и конец `workshop_order.py`, динамические вызовы по строке в сторонних модулях и из shell.
