# odoo-19.0 (справочник Odoo 19)

- **Путь:** `skills/odoo-19.0/` — `SKILL.md` (75 строк, таблица) + 18 файлов
  `references/odoo-19-*-guide.md` (244–642 строки, всего ~7 400)
- **Вердикт:** **отклонить как источник**, взять идею «файла ловушек версии»

## Что это

Индекс-таблица «тема → файл» и 18 руководств: actions, controllers, data,
decorators, development, fields, manifest, migration, mixins, models, OWL,
performance, reports, security, testing, transactions, translation, views.
Ссылок на исходник с номерами строк нет; в `SKILL.md` заявлено «основано
на анализе исходников Odoo 19», но перечислены пути, которых в 19.0 как
реализации уже нет (`odoo/models.py` и др., теперь `odoo/orm/*`).

## Точность (сверка с `odoo/odoo@19.0`, подробно в `../notes.md`)

- Верно: `models.Constraint` / `models.Index`, отказ от `_sql_constraints`,
  `res.groups.privilege` и `privilege_id`, `@api.private`,
  `from odoo.fields import Domain`, `env.execute_query(SQL)`, `_read_group`,
  `search_fetch`.
- Неверно или устарело: хуки манифеста в формате `module.func`,
  момент `uninstall_hook`, `type='json'` без пометки об алиасе `jsonrpc`,
  `groups_id` у отчётов/действий (в 19.0 `group_ids`), раздел
  `@api.returns` (декоратора нет), `states=` у кнопок (ошибка с 17.0),
  таблица «изменения Odoo 19», где перечислены изменения 14–18.
- Не нашёл (поиском, не доказано отсутствие): `@api.readonly`,
  `check_company`, `formatted_read_group`, переход `res.users.groups_id` →
  `group_ids`, удалённые поля партнёра (`mobile`, `title`), из-за которых
  в нашем пилоте не ставился модуль.

## Сравнение с нашим

- `boost:source-check` требует первичный источник и цитату; этот
  справочник — вторичный текст без ссылок, по правилам source-check он
  источником не считается. Подгрузка его в контекст могла бы *увеличить*
  долю устаревших API (не мерили).
- Context7 (`/websites/odoo/19.0`) даёт официальную документацию — лучше.

## Что взять

Источник: `skills/odoo-19.0/references/*@634b2db` (как антипример).
Куда: `plugins/boost/skills/source-check/references/odoo19-traps.md`.
Как: только идея, данные — наша сверка с `odoo/odoo@e0b25b7`.

Не текст, а идею: короткий файл значений «ловушки 19.0» с путём и строкой
исходника на каждую, рядом с `boost:source-check`
(`references/odoo19-sources.md` или отдельный `odoo19-traps.md`).
Наполнять своей сверкой (таблица в `../notes.md`) и находками пилота.
Метод остаётся в скилле, значения в файле (принцип №29).
