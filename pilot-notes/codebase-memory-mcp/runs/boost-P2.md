# boost-P2

cost $0.098, turns 8, time 23.6s, in 8, cache_create 14445, cache_read 150131, out 2471

Переименование затрагивает 3 места в коде и миграцию данных. Поле определено только в `td_workshop`, а упоминается ещё в `td_workshop_sale`. В `td_workshop_portal`, тестах, правах, `ir.rule` и CSV упоминаний нет (искал `\bdiscount\b` по всему репозиторию, кроме `.git`).

| # | path:line | Что произойдёт |
|---|---|---|
| 1 | `td_workshop/models/workshop_order.py:34` | Определение поля. |
| 2 | `td_workshop/models/workshop_order.py:48` | `order.discount` в `_compute_amount_total` даст `AttributeError` при пересчёте `amount_total`. Это поле хранимое (`store=True`), так что упадёт пересчёт при изменении `line_ids.subtotal`. |
| 3 | `td_workshop/views/workshop_order_views.xml:66` | `<field name="discount"/>` в форме. Установка или обновление модуля упадёт с ошибкой валидации вью. Это же сломает наследующую вью `td_workshop_sale.view_workshop_order_form_sale`, потому что она строится поверх этой формы. |
| 4 | `td_workshop_sale/models/workshop_order.py:24` | В `self.discount` нужно поменять имя. Ключ `"discount"` в словаре менять нельзя: это поле `sale.order.line` из ядра. Если переименовать и его, создание КП сломается. Без правки `action_create_quotation` упадёт с `AttributeError`. |

**Данные.** В БД колонка `discount` останется со старыми значениями, а новая колонка создастся пустой. Все скидки в существующих заказах обнулятся, и `amount_total` при следующем пересчёте станет без скидки. Нужен pre-migration скрипт в `td_workshop` с `ALTER TABLE td_workshop_order RENAME COLUMN` (имя таблицы не проверял) и повышением версии в манифесте. Либо можно задать новому полю `oldname`-подобную миграцию вручную, но автоматического переноса в Odoo 19 нет.

**Попутно (не из-за переименования).** В `@api.depends("line_ids.subtotal")` на `td_workshop/models/workshop_order.py:44` нет самого поля скидки. Сейчас `amount_total` не пересчитывается при смене скидки. Добавьте новое имя поля в `depends`, пока всё равно правите строку.

**Где не искал:** данные в БД (`ir.filters`, серверные действия, автоматизации, сохранённые отчёты); JS/OWL и QWeb-отчёты искал только общим `\bdiscount\b`, динамические обращения (`getattr`, `env[var]`, строки с именем поля, собранные из частей) этим поиском не найти; ядро и enterprise; другие репозитории и внешние интеграции, которые могут писать в `discount` по API или XML-RPC.

Не проверено / риск: имя таблицы в SQL выше; вью `:66` читал только по выводу скрипта и grep; поведение миграции на реальной БД не запускал.
