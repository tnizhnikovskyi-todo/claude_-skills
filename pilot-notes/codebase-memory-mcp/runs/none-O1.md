# none-O1

cost $0.057, turns 5, time 16.5s, in 6, cache_create 7186, cache_read 98880, out 1854

В аддонах sale, stock, account, product и base (`odoo/addons/base`) нашлись пять мест, которые определяют, расширяют или делегируют `product.template`. Нашёл поиском по `_inherit`, `_inherits` и `_name` в `.py`-файлах этих аддонов, сами файлы целиком не читал.

| Модуль | Файл | Способ | Что это |
|---|---|---|---|
| `product` | `addons/product/models/product_template.py:19` | `_name = 'product.template'` | Определение самой модели, не расширение. |
| `product` | `addons/product/models/product_product.py:19` | `_inherits = {'product.template': 'product_tmpl_id'}` | Делегирование: `product.product` берёт поля шаблона через `product_tmpl_id`. |
| `sale` | `addons/sale/models/product_template.py:11` | `_inherit = 'product.template'` | Расширение класса. |
| `stock` | `addons/stock/models/product.py:827` | `_inherit = 'product.template'` | Расширение класса. В том же файле выше, вероятно, расширяется `product.product`. |
| `account` | `addons/account/models/product.py:38` | `_inherit = "product.template"` | Расширение класса. |

- **`base`:** в `odoo/addons/base` совпадений нет.
- **Расширений в списке нет:** `_inherit` как список с `product.template` и многострочные объявления `_inherit` / `_inherits` поиск не нашёл. Первый и второй запросы возвращали разные наборы совпадений, поэтому я отдельно перепроверил эти формы, они ничего не дали.
- **`comodel_name='product.template'`:** такие поля (Many2one, Many2many) встречаются во многих файлах. Это ссылки на модель, а не наследование, поэтому в таблицу я их не включил.
- **Другие модули:** `product_product.py` может быть единственным `_inherits` на `product.template` только в этих пяти аддонах. Остальные модули репозитория (`mrp`, `website_sale` и т. д.) я не проверял.
