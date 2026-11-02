---
type: llm
weight: 2
---
Ошибка 2 (падение крона): в `_cron_service_reminder` выражение
`today - vehicle.last_service_date > vehicle.service_interval_days`
сравнивает `timedelta` с `int` → TypeError, крон падает на первой же машине
с датой сервиса.
PASS, если ревью находит именно это (timedelta сравнивается с int / нужно
`.days` или `timedelta(days=...)`).
FAIL, если не находит.
