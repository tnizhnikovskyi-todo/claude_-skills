# Чек-лист аудита модуля Odoo 19
- `security/ir.model.access.csv`: строка на каждую модель.
- `ir.rule`: мультикомпания (`company_id in company_ids`), записи пользователя.
- `controllers/`: `auth='public'`, `sudo()`.
