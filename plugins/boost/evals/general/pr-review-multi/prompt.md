---
name: general/pr-review-multi
description: Ревью большого PR с тремя заложенными ошибками разного рода и корректными «приманками»
tags: [general, hard, review, odoo]
max_turns: 6
allowed_tools: [Read, Glob, Grep, Skill]
---

Сделай ревью PR в модуль `td_vehicle` (Odoo 19). Описание PR от автора:
«Добавил сервисные интервалы, крон-напоминание и публичную страницу статуса
машины для водителей. Всё протестировано вручную, просьба быстро аппрувнуть».
Перечисли проблемы по серьёзности, для каждой: где, почему, как исправить.

```diff
--- a/td_vehicle/__manifest__.py
+++ b/td_vehicle/__manifest__.py
@@ -1,10 +1,13 @@
 {
     "name": "TD Vehicle",
-    "version": "19.0.1.0.0",
+    "version": "19.0.1.1.0",
     "depends": ["base", "mail"],
     "data": [
         "security/ir.model.access.csv",
         "views/td_vehicle_views.xml",
+        "views/td_vehicle_service_views.xml",
+        "data/ir_cron.xml",
     ],
     "license": "LGPL-3",
 }
--- a/td_vehicle/models/td_vehicle.py
+++ b/td_vehicle/models/td_vehicle.py
@@ -1,4 +1,6 @@
-from odoo import api, fields, models
+from datetime import timedelta
+
+from odoo import api, fields, models


 class TdVehicle(models.Model):
@@ -12,6 +14,52 @@ class TdVehicle(models.Model):
     driver_id = fields.Many2one("res.partner")
     state = fields.Selection(
         [("draft", "Draft"), ("active", "Active"), ("sold", "Sold")],
         default="draft",
     )
+    service_ids = fields.One2many("td.vehicle.service", "vehicle_id")
+    last_service_date = fields.Date(
+        compute="_compute_last_service", store=True,
+    )
+    service_interval_days = fields.Integer(default=180)
+    service_due = fields.Boolean(compute="_compute_service_due")
+    service_cost_total = fields.Float(
+        compute="_compute_service_cost_total", store=True,
+    )
+
+    @api.depends("service_ids.date")
+    def _compute_last_service(self):
+        for vehicle in self:
+            dates = vehicle.service_ids.mapped("date")
+            vehicle.last_service_date = max(dates) if dates else False
+
+    @api.depends("last_service_date", "service_interval_days")
+    def _compute_service_due(self):
+        today = fields.Date.context_today(self)
+        for vehicle in self:
+            if not vehicle.last_service_date:
+                vehicle.service_due = True
+                continue
+            vehicle.service_due = (
+                vehicle.last_service_date
+                + timedelta(days=vehicle.service_interval_days) <= today
+            )
+
+    @api.depends("service_ids")
+    def _compute_service_cost_total(self):
+        for vehicle in self:
+            vehicle.service_cost_total = sum(vehicle.service_ids.mapped("cost"))
+
+    @api.model
+    def _cron_service_reminder(self):
+        today = fields.Date.context_today(self)
+        vehicles = self.search([("state", "=", "active")])
+        for vehicle in vehicles:
+            if not vehicle.last_service_date:
+                continue
+            if today - vehicle.last_service_date > vehicle.service_interval_days:
+                vehicle.message_post(
+                    body=self.env._("Service is due for %s", vehicle.name),
+                    partner_ids=vehicle.driver_id.ids,
+                )
+
+
+class TdVehicleService(models.Model):
+    _name = "td.vehicle.service"
+    _description = "Vehicle service"
+    _order = "date desc"
+
+    vehicle_id = fields.Many2one("td.vehicle", required=True, ondelete="cascade", index=True)
+    date = fields.Date(required=True, default=fields.Date.context_today)
+    cost = fields.Float()
+    note = fields.Text()
--- /dev/null
+++ b/td_vehicle/controllers/main.py
@@ -0,0 +1,27 @@
+from odoo import http
+from odoo.http import request
+
+
+class VehicleStatusController(http.Controller):
+
+    @http.route("/vehicle/status", type="http", auth="public", website=False)
+    def vehicle_status(self, plate=None, **kwargs):
+        if not plate:
+            return request.not_found()
+        vehicles = request.env["td.vehicle"].sudo().search_read(
+            [("plate", "ilike", plate)],
+            ["name", "plate", "state", "driver_id", "last_service_date",
+             "service_cost_total", "company_id"],
+        )
+        return request.make_json_response(vehicles)
+
+    @http.route("/my/vehicle/<int:vehicle_id>", type="http", auth="user")
+    def my_vehicle(self, vehicle_id, **kwargs):
+        # Права проверяются ORM: без sudo() пользователь получит
+        # AccessError, если запись ему недоступна.
+        vehicle = request.env["td.vehicle"].browse(vehicle_id).exists()
+        if not vehicle:
+            return request.not_found()
+        return request.make_json_response(
+            vehicle.read(["name", "plate", "state", "last_service_date"])
+        )
--- /dev/null
+++ b/td_vehicle/data/ir_cron.xml
@@ -0,0 +1,11 @@
+<odoo>
+    <record id="ir_cron_vehicle_service_reminder" model="ir.cron">
+        <field name="name">Vehicle: service reminder</field>
+        <field name="model_id" ref="model_td_vehicle"/>
+        <field name="state">code</field>
+        <field name="code">model._cron_service_reminder()</field>
+        <field name="interval_number">1</field>
+        <field name="interval_type">days</field>
+    </record>
+</odoo>
--- a/td_vehicle/security/ir.model.access.csv
+++ b/td_vehicle/security/ir.model.access.csv
@@ -1,3 +1,5 @@
 id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
 access_td_vehicle_user,td.vehicle user,model_td_vehicle,base.group_user,1,1,1,0
 access_td_vehicle_manager,td.vehicle manager,model_td_vehicle,base.group_system,1,1,1,1
+access_td_vehicle_service_user,td.vehicle.service user,model_td_vehicle_service,base.group_user,1,1,1,0
+access_td_vehicle_service_manager,td.vehicle.service manager,model_td_vehicle_service,base.group_system,1,1,1,1
```
