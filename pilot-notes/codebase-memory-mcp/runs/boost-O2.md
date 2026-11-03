# boost-O2

cost $0.082, turns 5, time 15.1s, in 8, cache_create 12920, cache_read 146069, out 1516

Карта: в репозитории 4 аддона (`base`, `account`, `product`, `stock`, `sale`; ещё 3 тестовых манифеста в `base/tests`). Модуль `sale_stock` и другие расширения `sale.order` здесь отсутствуют.

## Определение и переопределения `sale.order._action_confirm`

| Роль | Модуль | Файл:строка |
|---|---|---|
| Определяет (пустой хук) | `sale` | `addons/sale/models/sale_order.py:1237` |
| Переопределяет | не найдено | — |

Метод `sale.order._action_confirm` определён один раз, с пустым телом. Его docstring говорит, что метод нужно расширять, когда подтверждение должно создавать другие документы. Переопределений `sale.order._action_confirm` в этих аддонах нет. В реальной базе его расширяют `sale_stock`, `sale_project` и другие, но их здесь нет.

## Кто вызывает

Единственный вызов `sale.order._action_confirm` находится в `sale.order.action_confirm`: `addons/sale/models/sale_order.py:1196`, `self.with_context(context)._action_confirm()`. Перед ним метод проверяет `_confirmation_error_message()` и пишет значения из `_prepare_confirmation_values()`. В контексте он убирает `default_name` и `default_user_id`. Если указан `send_email`, он отправляет письмо.

Публичный `action_confirm` вызывают:
- кнопки в `addons/sale/views/sale_order_views.xml:308` и `:323`;
- `addons/sale/models/sale_order.py:1304`, через `with_context(send_email=True)`;
- `addons/sale/models/payment_transaction.py:127`, при автоподтверждении после платежа;
- тесты и `addons/account/tests/common.py:907`.

## Совпадения по имени, которые не относятся к `sale.order`

`stock.move._action_confirm` определён в `addons/stock/models/stock_move.py:1701`. Его вызывают `stock_move.py` (строки 1273, 1793, 1795, 2266, 2352), `stock_rule.py:317` и `stock_picking.py` (строки 1215, 1601). Это другая модель с тем же именем метода.

## Где не искал

- Ядро Odoo 19 за пределами этих аддонов и enterprise. Именно там живут `sale_stock`, `sale_project` и другие, которые переопределяют метод в реальной установке.
- Другие репозитории и `addons_path`.
- Данные БД: серверные действия и автоматизации.
- Динамические вызовы вроде `getattr` или `env[var]`.
- Тесты я исключил из списка переопределений. Для вызовов `_action_confirm` с `/tests/` я их тоже отфильтровал.
