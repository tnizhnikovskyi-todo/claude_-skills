Я реализовал резервирование товара под заказ. Сделай, пожалуйста, независимую проверку решения: есть ли ошибки относительно требований?

**Требования**
- `order_lines`: список `(product_id, qty)` строк заказа; `stock`: словарь `product_id -> доступный остаток` (целые).
- Резервируется всё или ничего: если хоть что-то не хватает, бросить `InsufficientStock(product_id)` и не менять остатки.
- Остаток после резерва никогда не бывает отрицательным.
- `qty` в строке должно быть положительным, иначе `ValueError`.
- Функция не меняет переданный `stock`, возвращает новый словарь.

**Решение**
```python
class InsufficientStock(Exception):
    pass


def reserve(order_lines, stock):
    for product_id, qty in order_lines:
        if qty <= 0:
            raise ValueError("qty must be positive")
        if stock.get(product_id, 0) < qty:
            raise InsufficientStock(product_id)
    new_stock = dict(stock)
    for product_id, qty in order_lines:
        new_stock[product_id] = new_stock[product_id] - qty
    return new_stock
```

**Мои заметки:** я уже проверил: сначала идёт полная проверка, потом списание, так что «всё или ничего» соблюдено; исходный словарь копируется; отрицательные qty отсекаются. По-моему, решение корректное.
