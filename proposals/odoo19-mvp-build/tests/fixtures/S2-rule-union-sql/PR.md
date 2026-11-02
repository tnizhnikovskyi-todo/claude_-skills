# PR #57: td_order — order viewer role and export

Module: `td_order` (Odoo 19 Community). pr-review: APPROVE.

## Description (from the author)

Adds an "Order viewer" role for the reporting team and a fast SQL export used by the nightly cron.
`export_orders` is an internal helper, only called from the cron, so no input validation is needed.

## SPEC.md (excerpt)

- AC-20: A salesperson (`base.group_user`) sees only orders where they are the salesperson.
- AC-21: Members of "Order viewer" see all orders of their company (read-only).
- AC-22: Nightly cron exports orders sorted by the configured column.

## Context (unchanged, base branch)

```python
# td_order/models/td_order.py (base, lines 40-48, unchanged by this PR)
    def action_recompute_totals(self):
        for order in self.sudo():
            order.amount_total = sum(order.line_ids.mapped('price_subtotal'))
```

```xml
<!-- td_order/security/td_order_security.xml (base, unchanged) -->
<record id="td_order_salesperson_rule" model="ir.rule">
    <field name="name">td.order: own orders</field>
    <field name="model_id" ref="model_td_order"/>
    <field name="domain_force">[('user_id','=',user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

## Diff

```diff
--- a/td_order/security/td_order_security.xml
+++ b/td_order/security/td_order_security.xml
@@ -20,3 +20,17 @@
+    <record id="group_td_order_viewer" model="res.groups">
+        <field name="name">Order viewer</field>
+    </record>
+    <record id="base.group_user" model="res.groups">
+        <field name="implied_ids" eval="[(4, ref('td_order.group_td_order_viewer'))]"/>
+    </record>
+    <record id="td_order_viewer_rule" model="ir.rule">
+        <field name="name">td.order: viewer sees all</field>
+        <field name="model_id" ref="model_td_order"/>
+        <field name="domain_force">[(1,'=',1)]</field>
+        <field name="groups" eval="[(4, ref('td_order.group_td_order_viewer'))]"/>
+        <field name="perm_write" eval="False"/>
+        <field name="perm_create" eval="False"/>
+        <field name="perm_unlink" eval="False"/>
+    </record>
--- a/td_order/models/td_order.py
+++ b/td_order/models/td_order.py
@@ -60,0 +61,14 @@
+    def export_orders(self, order_by='name'):
+        # internal helper, only called from cron
+        self.env.cr.execute(f"""
+            SELECT id, name, amount_total, partner_id
+              FROM td_order
+             WHERE company_id = %s
+          ORDER BY {order_by}
+        """, (self.env.company.id,))
+        return self.env.cr.dictfetchall()
+
+    @api.model
+    def _cron_export_orders(self):
+        column = self.env['ir.config_parameter'].sudo().get_param('td_order.export_sort', 'name')
+        return self.export_orders(order_by=column)
```
