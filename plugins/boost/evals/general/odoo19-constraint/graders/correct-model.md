---
type: llm
---
Проверь итоговый код модели в ответе (Odoo 19).
PASS, если выполнено всё:
- уникальность (partner_id, code) задана через атрибут класса
  `models.Constraint("UNIQUE(partner_id, code)", ...)` или `models.UniqueIndex(...)`;
- неотрицательность qty задана через `models.Constraint("CHECK(qty >= 0)", ...)`
  (допустим дополнительно `@api.constrains`, но не вместо SQL-ограничения);
- в коде нет присваивания `_sql_constraints = [...]`.
FAIL, если используется `_sql_constraints` или одно из ограничений отсутствует.
