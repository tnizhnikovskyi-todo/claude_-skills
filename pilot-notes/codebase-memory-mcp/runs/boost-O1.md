# boost-O1

cost $0.096, turns 10, time 18.6s, in 10, cache_create 14319, cache_read 187384, out 1990

В аддонах sale, stock, account и product `product.template` расширяют три модуля через `_inherit`. Один модуль делегирует ему через `_inherits`. Определена сама модель в `product`.

| Роль | Модуль | Файл:строка | Класс | Способ |
|---|---|---|---|---|
| Определяет | product | `addons/product/models/product_template.py:19` | — | `_name = 'product.template'` |
| Расширяет | sale | `addons/sale/models/product_template.py:11` | `ProductTemplate` | `_inherit = 'product.template'` |
| Расширяет | stock | `addons/stock/models/product.py:827` | `ProductTemplate` | `_inherit = 'product.template'` |
| Расширяет | account | `addons/account/models/product.py:38` | `ProductTemplate` | `_inherit = "product.template"` |
| Делегирует | product | `addons/product/models/product_product.py:19` | `ProductProduct` | `_inherits = {'product.template': 'product_tmpl_id'}` |

Что это значит на практике:
- **Расширение.** Три модуля добавляют поля и методы прямо в `product.template`, новой модели они не создают.
- **Делегирование.** В `product.product` (вариант товара) поля шаблона видны напрямую и хранятся в шаблоне. Через `product_tmpl_id` связаны эти две модели.
- **Другие `_inherits`.** В `product/models/product_document.py:11` делегирование идёт на другую модель, не на `product.template`.

Я искал только в `.py`-файлах этих четырёх аддонов, сначала в однострочных объявлениях, потом отдельно по `_inherits`. Список вида `_inherit = ['product.template', ...]` на нескольких строках мог не попасть в поиск. Дочерние модели `product.template.attribute.*` отдельные (у них свой `_name`), они не наследники.

**Где не искал:**
- ядро Odoo и enterprise;
- другие аддоны этого клона, кроме sale, stock, account и product;
- XML-вью (например, `inherit_id` на формы `product.template`);
- JS и QWeb;
- данные в БД;
- динамические имена вроде `env[var]`.
