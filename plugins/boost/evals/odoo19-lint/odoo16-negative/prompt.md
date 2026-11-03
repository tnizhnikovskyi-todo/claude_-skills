---
name: odoo19-lint/odoo16-negative
description: "Негатив: правка вью в модуле Odoo 16. Правила 19 тут вредны (attrs/states в 16 верны), скилл не должен срабатывать"
tags: [odoo19-lint, negative, odoo]
max_turns: 8
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

Модуль `td_repair` на **Odoo 16** (`'version': '16.0.1.2.0'` в манифесте,
продакшн на 16, миграции не планируется). Форма:

```xml
<record id="td_repair_order_view_form" model="ir.ui.view">
    <field name="name">td.repair.order.form</field>
    <field name="model">td.repair.order</field>
    <field name="arch" type="xml">
        <form>
            <header>
                <button name="action_confirm" type="object" string="Confirm"/>
                <field name="state" widget="statusbar"/>
            </header>
            <sheet>
                <group>
                    <field name="name"/>
                    <field name="partner_id"/>
                    <field name="technician_note"/>
                </group>
            </sheet>
        </form>
    </field>
</record>
```

Нужно: кнопка «Confirm» видна только в состоянии `draft`, а поле
`technician_note` скрыто, пока заказ в `draft`. Запись файлов отключена:
покажи изменённый XML в ответе.
