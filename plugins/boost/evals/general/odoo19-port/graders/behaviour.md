---
type: llm
weight: 2
focus: { source: file, path: td_vehicle/views/td_vehicle_views.xml }
---
Это вид модели td.vehicle после переноса на Odoo 19. Проверь, что поведение
старого вида сохранено новыми выражениями:
- кнопка Activate видна только в state = draft, Sell только в state = active
  (атрибут invisible с выражением, например invisible="state != 'draft'");
- plate только для чтения, если state != 'draft' (readonly="state != 'draft'");
- driver_id скрыт при state = 'sold';
- список строк затрат редактируемый (editable="bottom").
PASS, если все четыре пункта выполнены. FAIL, если хотя бы одно условие
потеряно или инвертировано.
