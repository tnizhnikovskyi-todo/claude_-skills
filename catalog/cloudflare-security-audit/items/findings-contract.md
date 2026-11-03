# Контракт находок: `report-schema.json` + валидаторы

Файлы: `skills/security-audit/report-schema.json`, `validate-findings.cjs`,
`validate-coverage-ledger.cjs` (+ тесты) @ `c1c8a8c` (MIT, Cloudflare).

## Как устроено

`findings.json` — массив, `oneOf` из трёх веток со своим набором полей:

| Вердикт | Обязательно | Запрещено |
|---|---|---|
| `confirmed` | `root_cause`, `intended_behavior`, `trace`, `evidence`, `conditions` (enum: `authentication_level`, `authorization_role`, `user_interaction`, `system_configuration`, `data_state`, …), `execution.observed_result`, `remediation`, `severity` (likelihood / impact / overall ≤ impact), `confidence` | `blockers`, `validation_plan`, `reason` |
| `needs_validation` | `claimed_root_cause`, `trace`, `evidence`, `blockers`, `validation_plan.local` и/или `.deployment` | **severity**, `execution`, `remediation` |
| `rejected` | `claimed_root_cause`, `trace`, `evidence`, `reason` | severity, план, блокеры |

- `trace`: `entrypoint` → `propagation`* → `sink`, у каждого шага `file`, `line`,
  `scope`, `description`.
- `fingerprint` стабилен между состояниями и прогонами, без строки, волны,
  агента, severity (`^[A-Za-z0-9][A-Za-z0-9._:/@+-]*$`).
- Валидаторы на Node без зависимостей, только чтение файла (лимиты: 5 МиБ,
  1000 записей, глубина 64). Проверяют формат и согласованность с ledger, но
  не истинность — это они сами пишут.

## Сравнение с нашим `security-review`

| | Их | Наш (Strix-версия) |
|---|---|---|
| Состояния | confirmed / needs_validation / rejected | confirmed / open_proof_gap / ruled_out |
| `rejected` vs `ruled_out` | опровергнутый кандидат, хранится, чтобы не повторять | безопасная область с названным контролем |
| Severity у неподтверждённого | нет | есть, неизвестная экспозиция снижает confidence |
| Условия | закрытый enum | свободный текст `Severity change` |
| План закрытия пробела | `local` и `deployment` раздельно | «одна проверка, которая закрывает» |
| Машиночитаемость | JSON + валидатор | markdown |
| Повторный прогон | fingerprint, перенос, перепроверка | «iter N» критиков, без сопоставления |

## Что берём

1. **План закрытия пробела в двух частях** для `open_proof_gap`:
   «локально» (тест `HttpCase`/`TransactionCase` с `with_user(portal)` на
   тестовой БД) и «на инстансе» (что посмотреть владельцу: членство в группах,
   `proxy_mode`, `dbfilter`, `list_db` → это уже `config-review`).
2. **Повторный аудит по fingerprint.** После правок `code-dev` таблица:
   fingerprint прошлого прогона → закрыт (какой шаг теперь падает) / остался /
   новый. Изменённый код → перепроверить, а не переносить вердикт.
3. **Закрытый список условий** как подсказка для `Severity change`
   (роль, взаимодействие пользователя, конфигурация, состояние данных, время).

## Что не берём

- Правило «нет severity у неподтверждённого»: для ворот перед деплоем наше
  правило (пробел на BLOCK-поверхности → REQUEST CHANGES) строже и нужнее.
- JSON и валидаторы: в цепочке `odoo19-mvp-build` нет потребителя JSON;
  Node-валидатор ради markdown-отчёта — лишняя зависимость.
