# odoo-test-writer

- **Путь:** `skills/odoo-test-writer/` — `SKILL.md` (71 строка) +
  `ODOO-TESTING-SOP.md` (218) + `ODOO-TESTING-EXAMPLES.md` (279)
- **Вердикт:** **взять 2–3 пункта** в `odoo19-mvp-build:testing`, примеры
  не брать

## Что это

Выбор базового класса (`TransactionCase` по умолчанию,
`AccountTestInvoicingCommon` для учёта, `Form` для onchange/дефолтов,
`HttpCase` для браузера, `SingleTransactionCase` только для чтения),
структура `tests/`, теги `post_install`/`-at_install`, моки на границе
внешних сервисов, тесты прав через `with_user`, `assertQueryCount`,
чек-лист завершения.

## Ошибки для Odoo 19.0

- Пример создаёт пользователя с `"groups_id": [(6, 0, …)]` — в 19.0 поле
  `group_ids`, тест упадёт. Идиоматичнее `new_test_user(env, groups=…)`
  (`odoo/tests/common.py:195`), он в навыке не упомянут.
- `assertQueryCount(__limit__=5)` — такого ключа нет; именованные
  аргументы это логины, ожидание остаётся 0, сравнение на равенство.

## Полезное (своими словами)

- «Каждый новый `test_*.py` должен импортироваться в `tests/__init__.py`,
  иначе раннер его не найдёт», и «не импортировать `tests` из корневого
  `__init__.py`».
- «Мокать там, где используется, а не где определено; проверять и
  состояние, и вызовы мока».
- «Для изменений прав — реальные пользователи, группы, компании через
  `with_user`».

## Сравнение с нашим

Текст `odoo19-mvp-build:testing` недоступен: в контейнере его нет,
подключить приватный `todoltd/claude-methodology-marketplace` не дала
система прав. Сравнение только по описанию. Проверить при доступе.

## Что взять

Источник: `skills/odoo-test-writer/SKILL.md@634b2db`,
`ODOO-TESTING-SOP.md@634b2db`. Куда: `odoo19-mvp-build:testing` через
`proposals/`. Как: только идея своими словами (лицензии нет). Плюс наше из
сверки: `new_test_user(env, groups='…')` и `group_ids` в 19.0.
