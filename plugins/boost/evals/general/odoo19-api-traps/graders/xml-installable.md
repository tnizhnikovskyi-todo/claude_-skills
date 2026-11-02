---
type: llm
weight: 5
focus: { source: file, path: td_vehicle/security/td_vehicle_security.xml }
---
Это XML с группами для Odoo 19. В Odoo 19 у модели `res.groups` нет полей
`users` и `category_id` (их заменили `user_ids` и `privilege_id`, раздел
прав задаётся записью `res.groups.privilege`, у которой есть `category_id`);
у `res.users` нет `groups_id` (теперь `group_ids`). Запись с
несуществующим полем ломает установку модуля.
PASS, если ни одна запись `res.groups` не использует поля `users`,
`category_id` или `groups_id`, ни одна запись `res.users` не использует
`groups_id`, менеджеры включают пользователей (implied_ids), и администратор
добавлен через `user_ids` группы (или `group_ids` пользователя).
FAIL, если есть хотя бы одно поле, которого нет в Odoo 19, или требование не выполнено.
