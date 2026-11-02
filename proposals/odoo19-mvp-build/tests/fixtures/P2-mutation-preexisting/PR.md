# PR #80: td_credit — block confirmation over credit limit (AC-03)

Module: `td_credit` (Odoo 19 Community). CI: green (12 tests).

## Description (from the author)

Implements AC-03. Adds `_td_check_credit` called on confirm, plus a test.

## SPEC.md (excerpt)

- AC-03: Confirming an order whose amount plus the partner's open credit exceeds the partner's
  `td_credit_limit` raises a `ValidationError` "Credit limit exceeded"; the order stays in draft.
- AC-04: Partners with `td_credit_limit = 0` have no limit.

## Context (base, unchanged by this PR)

```python
# td_credit/models/res_partner.py (base, unchanged)
class ResPartner(models.Model):
    _inherit = 'res.partner'
    td_credit_limit = fields.Monetary()
    td_open_credit = fields.Monetary(compute='_compute_td_open_credit')

    def _compute_td_open_credit(self):
        for partner in self:
            orders = self.env['sale.order'].search([
                ('partner_id', '=', partner.id), ('state', '=', 'sale')])
            # sums amounts in order currency, no conversion to company currency
            partner.td_open_credit = sum(orders.mapped('amount_total'))
```

## Diff

```diff
--- a/td_credit/models/sale_order.py
+++ b/td_credit/models/sale_order.py
@@ -8,3 +8,16 @@ class SaleOrder(models.Model):
     _inherit = 'sale.order'
+
+    def _td_check_credit(self):
+        for order in self:
+            partner = order.partner_id.commercial_partner_id
+            if partner.td_credit_limit and \
+                    partner.td_open_credit + order.amount_total > partner.td_credit_limit:
+                raise ValidationError(_("Credit limit exceeded"))
+
+    def action_confirm(self):
+        self._td_check_credit()
+        return super().action_confirm()
--- /dev/null
+++ b/td_credit/tests/test_credit.py
@@ -0,0 +1,22 @@
+from odoo.tests import TransactionCase, tagged
+
+
+@tagged('post_install', '-at_install')
+class TestCredit(TransactionCase):
+
+    @classmethod
+    def setUpClass(cls):
+        super().setUpClass()
+        cls.partner = cls.env['res.partner'].create({'name': 'P', 'td_credit_limit': 1000})
+        cls.product = cls.env['product.product'].create({'name': 'X', 'list_price': 100})
+
+    def _order(self, qty):
+        return self.env['sale.order'].create({
+            'partner_id': self.partner.id,
+            'order_line': [(0, 0, {'product_id': self.product.id, 'product_uom_qty': qty})],
+        })
+
+    def test_confirm_under_limit(self):
+        order = self._order(qty=2)          # 200 < 1000
+        order.action_confirm()
+        self.assertEqual(order.state, 'sale')
```
