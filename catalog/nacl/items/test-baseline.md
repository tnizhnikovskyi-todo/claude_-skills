# Baseline тестов и запрет APPROVE без доказательств (`nacl-tl-review` Step 6)

- **Источник:** `nacl-tl-review/SKILL.md`, «Step 6: Run Tests and Check Author Independence», 6a/6a-baseline; `project-gap-closure.md` «Forbidden terminal success states»
- **Вердикт:** адаптировать (вставка в ревью/тестирование)

## Что это

1. **Только объявленная команда тестов.** Запускается то, что объявлено
   в проекте. Если команды нет, ревью останавливается как `NO_INFRA` и
   `APPROVED` запрещён. Сломанный раннер — `RUNNER_BROKEN`, тоже без
   `APPROVED`.
2. **Baseline.** Утверждение «изменение сломало тесты» требует прогона
   на базе: `git worktree add <tmp> $(git merge-base HEAD main)`, тот же
   прогон, затем `new = after − before`. Нет базы — `UNVERIFIED (no
   baseline)`, классифицировать падения как новые или старые нельзя.
3. **Запрещённые «успехи».** `APPROVED — UNVERIFIED`, `QA_SKIP` и
   `UNVERIFIED` не считаются завершением.

## Перенос к нам

Вставка в `odoo19-mvp-build:testing` и `pr-review`:
- команда тестов Odoo — из README/CI модуля
  (`odoo-bin … --test-enable --test-tags /td_module`), не придумывать;
- при падениях прогнать то же на merge-base в отдельном worktree и
  показать таблицу «было / стало»;
- без зелёного прогона вердикт не выше «REQUEST CHANGES / не проверено».

Пересекается с нашими правилами («Не проверено / риск», `UNVERIFIED`),
но добавляет **процедуру baseline**, которой у нас нет. Цена: второй
прогон тестов, только когда есть падения.
