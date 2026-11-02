# Odoo 19: стандартный механизм вместо кастомного кода

Шпаргалка к шагу 3 лестницы. Слева то, что модель обычно пишет, справа то,
что делает платформа. Перед использованием сверяй API с документацией
Odoo 19 (https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html),
если в проекте подключён Context7 — через него (`/websites/odoo/19.0`).

| Соблазн | Стандартный механизм Odoo 19 |
|---|---|
| Новое поле с копией значения из партнёра + `onchange` + синхронизация в `write` | `phone = fields.Char(related='partner_id.phone')` (только показ; `store=True` только если нужен поиск/группировка) |
| Пересчёт суммы в `create`/`write` или кнопка «Пересчитать» | `compute='_compute_total'` + `@api.depends('line_ids.subtotal')`; `store=True`, если поле в фильтрах/отчётах |
| Проверка в переопределённом `write`/`create` с `raise` | `models.Constraint('CHECK(quantity >= 0)', 'Количество не может быть отрицательным')` (SQL) или `@api.constrains('field')` (Python, если нужна логика) |
| `_sql_constraints = [...]` | В Odoo 19 вместо него атрибут модели: `_qty_positive = models.Constraint('CHECK(quantity >= 0)', '...')`; индексы: `models.Index(...)` или `index=True` у поля |
| Копия модели/вида «под себя» | `_inherit = 'sale.order'`; вид через `inherit_id` + `xpath` |
| Свой счётчик номеров | `ir.sequence` + `default=lambda self: self.env['ir.sequence'].next_by_code(...)` или в `create` |
| Свой планировщик/поток | `ir.cron` (XML-запись с `model_id`, `code`) |
| Кнопка «отправить письмо/создать задачу» на Python | Сервер-экшен `ir.actions.server` или правило автоматизации `base.automation`, если модуль уже есть в `depends` |
| Свой журнал изменений | `_inherit = ['mail.thread']` + `tracking=True` у поля |
| Своя страница/контроллер для списка с фильтром | `ir.actions.act_window` с `domain`, `context` (`search_default_*`), фильтры и `group by` в `search`-виде |
| Smart-кнопка с ручным подсчётом в Python на каждую запись в цикле | `compute` с `_read_group` (без поиска в цикле) + `type="action"` на стандартный action |
| Проверка прав в коде метода | `ir.model.access.csv`, `ir.rule`, `groups=` у поля/кнопки/меню |
| Скрытие поля через JS | `invisible="state != 'draft'"`, `readonly=...`, `required=...` прямо в виде (в 17+ без `attrs`) |
| `tree` в XML | В 18+ вид называется `list` |
| Мультикомпания вручную | `check_company=True` у поля и `_check_company_auto = True` у модели |

## Когда кастомный код всё же нужен

- Бизнес-правило, которое нельзя выразить в SQL `CHECK` и в `@api.constrains`
  (например, зависит от внешнего API).
- Стандартный механизм даёт заметную проблему нагрузки на ожидаемом объёме
  (тогда пометь: `shortcut: ...` или объясни выбор одной строкой).
- ТР/спека прямо требует конкретную реализацию.

## Тест на рискованную логику в Odoo

```python
from psycopg2 import IntegrityError

from odoo.tests import TransactionCase, tagged
from odoo.tools import mute_logger


@tagged('post_install', '-at_install')
class TestRepairTotal(TransactionCase):
    def test_total(self):
        order = self.env['td.repair.order'].create({
            'name': 'R1',
            'line_ids': [(0, 0, {'quantity': 2, 'price_unit': 5.0})],
        })
        self.assertEqual(order.amount_total, 10.0)

    @mute_logger('odoo.sql_db')
    def test_negative_qty_rejected(self):
        order = self.env['td.repair.order'].create({'name': 'R2'})
        with self.assertRaises(IntegrityError):  # models.Constraint → ошибка БД
            order.line_ids = [(0, 0, {'quantity': -1, 'price_unit': 1.0})]
            self.env.flush_all()
```

Для `@api.constrains` вместо `IntegrityError` ловят
`odoo.exceptions.ValidationError`.

Один тест на правило, не «покрытие».
