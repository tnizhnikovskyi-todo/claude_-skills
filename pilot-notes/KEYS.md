# Ключ пилота: заложенные проблемы

Не копировать в прогоны: скиллы и модель не должны видеть этот файл.
Прогоны идут на копии `pilot/` в отдельном git-репозитории.

| # | Где | Проблема | Тяжесть | Что должно поймать |
|---|---|---|---|---|
| K1 | `td_workshop_portal/controllers/main.py` | `/repair/<int:id>` с `auth="public"` и `sudo().browse(id)`: любой перебором id видит имя клиента, телефон, сумму и заметки (IDOR) | безопасность, must-fix | repo-audit, security-review |
| K2 | `td_workshop/security/ir.model.access.csv` | Нет строк доступа для `td.workshop.close.wizard` (TransientModel): кнопка «Close» падает с AccessError у всех, кроме суперпользователя | баг | repo-audit, odoo-model-map |
| K3 | `td_workshop/models/res_partner.py` | `search_count` в цикле по партнёрам (N+1) в compute счётчика | нагрузка | repo-audit |
| K4 | `td_workshop/models/workshop_order.py` | `@api.depends("line_ids.subtotal")` без `discount`: при смене скидки хранимый `amount_total` не пересчитывается | баг, деньги | repo-audit, lean-change |
| K5 | `td_workshop/models/workshop_order.py` | `_legacy_recompute` нигде не вызывается и пишет в computed-поле вручную | мёртвый код | repo-audit |
| K6 | `workshop_order.py` и `td_workshop_sale/models/sale_order.py` | Дубль хелпера `_format_phone` в двух модулях | lean | repo-audit |
| K7 | `td_workshop/models/workshop_order.py` | `customer_phone` копируется в `create`/`onchange` вместо `related="partner_id.phone"`: расходится с партнёром | lean | repo-audit, lean-change |
| K8 | `td_workshop/models/workshop_order.py` | В cron `except Exception: pass`: ошибки отправки молча теряются | риск | repo-audit |
| K9 | `td_workshop/models/workshop_order.py` | `related="partner_id.mobile"`: в Odoo 19 поля `mobile` в `res.partner` нет (проверено по `odoo/addons/base/models/res_partner.py` веток 18.0 и 19.0). Модуль не установится | баг, установка | source-check, repo-audit |
| K10 | `td_workshop_sale/__manifest__.py` | Зависимость `stock` не используется | lean | repo-audit |
| K11 | `td_workshop/tests/` | Нет тестов на сумму со скидкой, права и мастер закрытия; `test_phone_copied` закрепляет поведение K7 | нет теста | repo-audit |
| K12 | `td_workshop/security/` | У `td.workshop.order.line` нет правила мультикомпании: через модель строк видны строки заказов чужой компании; `unlink` строк у пользователя разрешён, а у заказа нет | безопасность, средняя | repo-audit, odoo-model-map |
| K13 | `td_workshop_sale/models/workshop_order.py` | Строки без `product_id` (работы) молча пропускаются: в предложение не попадает оплата работ | баг, деньги | repo-audit |

Не ошибки (ловушки для ложных находок):
- `models.Constraint` вместо `_sql_constraints`, `<list>`, `invisible=`,
  `<chatter/>` написаны правильно для Odoo 19.
- Правила `technician` и `manager` для разных групп складываются через OR:
  менеджер видит всё, это задумано.

## Найдено сверх ключа (настоящие проблемы пилота)

| # | Где | Проблема | Кто нашёл |
|---|---|---|---|
| K14 | `td_workshop/__manifest__.py` | `product_id` ссылается на `product.product`, а `product` нет в `depends`: на чистой базе `-i td_workshop` падает на assert unknown comodel (подтверждено по `odoo/orm/fields_relational.py` 19.0 обоими прогонами source-check) | все прогоны |
| K15 | `td_workshop/security/workshop_security.xml` | В `group_workshop_manager` никто не входит, включая admin: администратор подчиняется правилу «техник видит свои и неназначенные» | аудит без плагина |
| K16 | `td_workshop/models/workshop_order.py` | `action_done`/`action_cancel` не проверяют текущий статус: через RPC можно закрыть отменённый и отменить закрытый заказ | оба аудита |
| K17 | там же | Скидка не ограничена 0–100: при 150% итог отрицательный | аудит с плагином |
| K18 | `td_workshop_sale` | Связь заказ ↔ предложение хранится в двух Many2one, синхронизация ручная: возможен дубль предложения | аудит с плагином |
