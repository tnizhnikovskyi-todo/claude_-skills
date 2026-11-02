Я добавил в портал Odoo 19 страницу счёта и скачивание PDF. Сделай независимую проверку решения — особенно доступа.

**Требования**
- Портальный пользователь (группа `base.group_portal`, у портала есть право read на `account.move`) видит **только счета своего коммерческого партнёра**: `invoice.partner_id.commercial_partner_id == user.partner_id.commercial_partner_id`.
- Чужой или несуществующий счёт → 404 (`NotFound`), и на странице, и на PDF.
- PDF рендерится отчётом `account.account_invoices`.

**Решение** (`controllers/portal.py`)
```python
from odoo import http
from odoo.http import request
from werkzeug.exceptions import NotFound


class InvoicePortal(http.Controller):

    def _get_own_invoice(self, invoice_id):
        invoice = request.env['account.move'].sudo().browse(invoice_id).exists()
        commercial = request.env.user.partner_id.commercial_partner_id
        if not invoice or invoice.partner_id.commercial_partner_id != commercial:
            raise NotFound()
        return invoice

    def _check_invoice_access(self, invoice_id):
        invoice = request.env['account.move'].browse(invoice_id).exists()
        if not invoice:
            raise NotFound()
        invoice.check_access_rights('read')
        return invoice.sudo()

    @http.route('/my/invoice/<int:invoice_id>', type='http', auth='user', website=True)
    def invoice_page(self, invoice_id, **kw):
        invoice = self._get_own_invoice(invoice_id)
        return request.render('portal_x.invoice_page', {'invoice': invoice})

    @http.route('/my/invoice/<int:invoice_id>/pdf', type='http', auth='user')
    def invoice_pdf(self, invoice_id, **kw):
        invoice = self._check_invoice_access(invoice_id)
        pdf, _ = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
            'account.account_invoices', [invoice.id])
        return request.make_response(pdf, headers=[('Content-Type', 'application/pdf')])
```

**Мои заметки:** оба маршрута `auth='user'`, у обоих есть проверка доступа до `sudo()`, несуществующий id даёт 404. Думаю, доступ закрыт корректно.
