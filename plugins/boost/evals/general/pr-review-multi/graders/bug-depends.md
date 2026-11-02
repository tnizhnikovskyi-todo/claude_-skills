---
type: llm
weight: 2
---
Ошибка 3 (данные): `_compute_service_cost_total` хранимый (`store=True`), но
зависит только от `service_ids`, а суммирует `service_ids.cost`. При
изменении стоимости существующей записи сервиса итог не пересчитается.
Нужно `@api.depends("service_ids.cost")`.
PASS, если ревью находит неполный `@api.depends` у service_cost_total.
FAIL, если не находит.
