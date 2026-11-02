Я добавил в Odoo 19 модель заявки на закупку с хранимой суммой. Проверь решение независимо: есть ли ошибки относительно требований?

**Требования**
- `td.purchase.request` со строками `td.purchase.request.line`.
- Сумма строки: `qty * price_unit * (1 - discount / 100)`, в валюте заявки, округлённая по валюте.
- `amount_total` заявки — сумма строк, **хранимое** поле (по нему строятся отчёты и поиск), всегда актуально после любой правки строк.
- Заявки с `amount_total` > `company_id.td_approval_limit` получают `state = 'to_approve'` при подтверждении, остальные `approved`.
- Скидка от 0 до 100 включительно, иначе ошибка валидации.

**Решение** (`models/purchase_request.py`)
```python
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PurchaseRequest(models.Model):
    _name = 'td.purchase.request'
    _description = 'Purchase Request'

    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda s: s.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id')
    line_ids = fields.One2many('td.purchase.request.line', 'request_id')
    amount_total = fields.Monetary(compute='_compute_amount_total', store=True)
    state = fields.Selection([('draft', 'Draft'), ('to_approve', 'To Approve'),
                              ('approved', 'Approved')], default='draft')

    @api.depends('line_ids.price_subtotal')
    def _compute_amount_total(self):
        for request in self:
            request.amount_total = sum(request.line_ids.mapped('price_subtotal'))

    def action_confirm(self):
        for request in self:
            limit = request.company_id.td_approval_limit
            request.state = 'to_approve' if request.amount_total >= limit else 'approved'


class PurchaseRequestLine(models.Model):
    _name = 'td.purchase.request.line'
    _description = 'Purchase Request Line'

    request_id = fields.Many2one('td.purchase.request', required=True, ondelete='cascade')
    currency_id = fields.Many2one(related='request_id.currency_id')
    product_id = fields.Many2one('product.product', required=True)
    qty = fields.Float(default=1.0)
    price_unit = fields.Monetary()
    discount = fields.Float()
    price_subtotal = fields.Monetary(compute='_compute_price_subtotal', store=True)

    @api.depends('qty', 'price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            amount = line.qty * line.price_unit * (1 - line.discount / 100)
            line.price_subtotal = line.currency_id.round(amount)

    @api.constrains('discount')
    def _check_discount(self):
        for line in self:
            if not 0 <= line.discount <= 100:
                raise ValidationError("Discount must be between 0 and 100.")
```

**Мои заметки:** оба compute хранимые, цепочка `depends` через `price_subtotal` пересчитывает заявку, округление по валюте есть, скидка валидируется. Думаю, всё корректно.
