---
name: general/pr-review-bug
description: Ревью PR с заложенной ошибкой (compute не присваивает значение во всех ветках)
tags: [general, review, odoo]
max_turns: 6
allowed_tools: [Read, Glob, Grep, Skill]
---

Сделай ревью этого PR (Odoo 19). Найди проблемы, отсортируй по серьёзности.

```diff
--- a/td_listing/models/td_listing.py
+++ b/td_listing/models/td_listing.py
@@ -1,9 +1,24 @@
 from odoo import api, fields, models

 class TdListing(models.Model):
     _name = "td.listing"
     _description = "Listing"

     partner_id = fields.Many2one("res.partner", required=True)
     state = fields.Selection([("draft", "Draft"), ("done", "Done")], default="draft")
+    line_ids = fields.One2many("td.listing.line", "listing_id")
+    total = fields.Float(compute="_compute_total", store=True)
+
+    @api.depends("line_ids.amount", "state")
+    def _compute_total(self):
+        for rec in self:
+            if rec.state == "done":
+                rec.total = sum(rec.line_ids.mapped("amount"))
+
+    def action_done(self):
+        for rec in self:
+            rec.state = "done"
+        return True
```
