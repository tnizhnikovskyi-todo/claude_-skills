# none-P2

cost $0.093, turns 9, time 26.1s, in 8, cache_create 12896, cache_read 140941, out 2751

Если переименовать `discount` в `td.workshop.order`, в репозитории придётся править 3 места. Ломается только вызов в `td_workshop_sale`. Остальные два места просто нужно переименовать вместе с полем.

| path:line | что произойдёт |
|---|---|
| `addons/td_workshop/models/workshop_order.py:34` | Определение поля. Здесь переименование и делается. |
| `addons/td_workshop/models/workshop_order.py:48` | `order.discount` в `_compute_amount_total`. Старое имя даст `AttributeError` при расчёте `amount_total`, то есть при создании и изменении строк. |
| `addons/td_workshop/views/workshop_order_views.xml:66` | `<field name="discount"/>` в форме. Odoo не загрузит вид, а при `-u` модуль не обновится. |
| `addons/td_workshop_sale/models/workshop_order.py:24` | `self.discount` в `action_create_quotation`. Старое имя даст `AttributeError`, и КП создать не получится. Ключ `"discount":` слева — поле `sale.order.line`, чужой модели. Его переименовывать нельзя. |

**Что менять не нужно:**
- Тесты (`tests/test_workshop_order.py`) поле не используют.
- Портал (`td_workshop_portal`) использует только `state`.
- `close_wizard.py`, `res_partner.py` и `ir.model.access.csv` поле не затрагивают.
- В `workshop_security.xml` есть только record rule по `technician_id`.

**Что изменится вне кода:**
- **Данные.** Без миграции (`pre-migrate` с `ALTER TABLE ... RENAME COLUMN` или `openupgrade.rename_fields`) колонка `discount` останется в БД. Новое поле создастся пустым, и скидки в существующих заказах пропадут.
- **Уже существующий дефект.** `@api.depends("line_ids.subtotal")` не включает `discount`. Сейчас `amount_total` не пересчитывается при смене скидки, и при переименовании это не изменится. Стоит добавить `discount` в `depends`, но это отдельное решение.

Как я искал: регистронезависимый поиск по `discount` по всему репозиторию (`addons`, `CLAUDE.md`, `README.md`). Затем я прочитал целиком оба `workshop_order.py`, `sale_order.py`, контроллер портала, `close_wizard.py` и тесты. Динамического доступа к полю (`getattr`, `_fields[...]`, `read([...])`) в коде нет. Шаблоны портала и остальные XML проверены только поиском по слову `discount`, целиком я их не читал.

Не проверено / риск: поля нет в репозитории, но оно может использоваться в БД и внешних системах. Это сохранённые фильтры и группировки (`ir.filters`), вручную добавленные виды, отчёты, автоматизации, внешние вызовы XML-RPC/JSON-RPC и экспорт или импорт. Их я не проверял. Для файлов `README.md`, `.gitignore`, `data/*.xml` и `res_partner_views.xml` у меня только результат поиска по слову, содержимое я не читал.
