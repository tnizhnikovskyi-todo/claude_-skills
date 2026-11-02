# PR #63: td_order — fix SQL injection in reference search + manager notes

Module: `td_order` (Odoo 19 Community). pr-review: APPROVE.

## Description (from the author)

1. Fixes the SQL injection reported in ticket TD-118 (`/td_order/search?sort=...`): we now reject
   any `sort` value containing `;` or `--`, so stacked queries and comments are impossible.
2. Adds an internal rich-text "Manager notes" field visible only to Order managers.
3. Adds a `color` field for kanban.

## SPEC.md (excerpt)

- AC-30: Logged-in internal users can search orders by reference and sort the result.
- AC-31: Order managers (`td_order.group_td_order_manager`) can keep formatted notes on an order.

## Context (base, unchanged)

```python
# td_order/controllers/main.py (base)
class TdOrderSearch(http.Controller):
    @http.route('/td_order/search', type='jsonrpc', auth='user')
    def search(self, ref='', sort='name', **kw):
        return request.env['td.order']._search_by_ref(ref, sort)
```
Group `td_order.group_td_order_manager` exists and is assigned to 3 users.

## Diff

```diff
--- a/td_order/models/td_order.py
+++ b/td_order/models/td_order.py
@@ -80,10 +80,15 @@
     @api.model
     def _search_by_ref(self, ref, sort):
-        self.env.cr.execute(
-            "SELECT id FROM td_order WHERE name ILIKE %s ORDER BY " + sort,
-            ('%' + ref + '%',))
+        if ';' in sort or '--' in sort:
+            raise UserError(_("Invalid sort"))
+        self.env.cr.execute(
+            "SELECT id FROM td_order WHERE name ILIKE %s ORDER BY " + sort,
+            ('%' + ref + '%',))
         return self.browse([r[0] for r in self.env.cr.fetchall()]).read(['name', 'amount_total'])
+
+    manager_note = fields.Html(sanitize=False, groups='td_order.group_td_order_manager')
+    color = fields.Integer()
--- a/td_order/views/td_order_views.xml
+++ b/td_order/views/td_order_views.xml
@@ -30,2 +30,4 @@
             <field name="partner_id"/>
+            <field name="color" widget="color_picker"/>
+            <field name="manager_note" groups="td_order.group_td_order_manager"/>
```
