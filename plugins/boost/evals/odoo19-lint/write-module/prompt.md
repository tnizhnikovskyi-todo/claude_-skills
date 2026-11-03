---
name: odoo19-lint/write-module
description: "Новый модуль Odoo 19 с нуля: естественный код по памяти о 16–18 ломает установку (мобильный и обращение клиента, группы, крон, уникальность, отображаемое имя, действие списка)"
tags: [odoo19-lint, positive, odoo, code]
max_turns: 16
timeout_seconds: 500
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Новый модуль `td_rental` для Odoo 19 (зависит от `mail`). Запиши файлы:

1. `td_rental/models/rental_order.py` — модель `td.rental.order`:
   `code` (уникален в пределах компании), `company_id`, `customer_id`
   (контакт), `date_start`, `date_end`, `state` (draft/ongoing/done);
   для показа на форме — `customer_mobile` (мобильный телефон клиента) и
   `customer_title` (обращение клиента из его карточки, например «Mister»);
   отображаемое имя записи — «<code> - <имя клиента>».
2. `td_rental/security/security.xml` — группы «Пользователь аренды» и
   «Менеджер аренды» в разделе прав «Аренда»; менеджер включает
   пользователя, пользователь включает `base.group_user`; администратора
   (`base.user_admin`) сразу добавить в менеджеры.
3. `td_rental/data/ir_cron.xml` — ежедневный крон `model._cron_close_overdue()`
   без ограничения числа запусков (метод добавь в модель: закрывает
   просроченные `ongoing`).
4. `td_rental/views/rental_views.xml` — список и форма заказа (на форме
   кнопка «Start» видна только в draft), действие с режимами список и
   форма, пункт меню.

Манифест и `__init__.py` не нужны. В ответе коротко: что сделано.
