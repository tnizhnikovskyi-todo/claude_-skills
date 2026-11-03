# none-O2

cost $0.097, turns 6, time 18.9s, in 8, cache_create 15758, cache_read 148351, out 1928

В этой копии аддонов `sale.order._action_confirm` вызывается из одного места и определяется тоже в одном. Переопределений нет.

**Кто вызывает**
- Единственный вызов: `addons/sale/models/sale_order.py:1196`, в публичном `action_confirm()`: `self.with_context(context)._action_confirm()`.
- Перед ним `action_confirm()` проверяет заказы через `_confirmation_error_message()` и валидирует аналитику. Затем пишет значения из `_prepare_confirmation_values()` (`state='sale'`, `date_order`) и убирает из контекста `default_name` и `default_user_id`.
- После вызова он блокирует заказ через `action_lock()`, если `_should_be_locked()` вернул True, и отправляет письмо при `send_email` в контексте.
- Сам `action_confirm()` вызывается из кнопки в `sale/views/sale_order_views.xml`, из `sale/models/payment_transaction.py` (подтверждение после оплаты) и из демо-данных `sale_demo.xml`. Это я определил по списку файлов с `action_confirm`, сами вхождения не открывал.

**Кто переопределяет**
- Сама база: `addons/sale/models/sale_order.py:1237`. Метод пустой, в нём только docstring: он нужен как точка расширения, и в нём заказ уже в состоянии `sale`.
- Других `def _action_confirm` в репозитории только один: `addons/stock/models/stock_move.py:1701`. Это метод `stock.move`, он не связан с `sale.order`. Его вызывают `stock_picking.py`, `stock_rule.py` и тесты, которых в выводе большинство.

В этой копии из аддонов, связанных с продажами, есть только `sale`. Нет `sale_stock`, `sale_mrp`, `sale_project`, `sale_loyalty` и других. Поэтому в полном наборе Odoo 19 переопределения у `sale.order._action_confirm` наверняка есть, но здесь их нет. Если нужен полный список, добавьте остальные аддоны в рабочую директорию, и я повторю поиск.
