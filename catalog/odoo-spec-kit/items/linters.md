# Линтеры `pre-commit` (odoo-spec-kit)

- **Тип:** конфигурация `pre-commit` + `.pylintrc` / `.pylintrc-mandatory` + `.ruff.toml` + `prettier.config.cjs`
- **Источник:** `focuz-ai/odoo-spec-kit@23df08b`; по составу — шаблон OCA (`oca-addons-repo-template`)
- **Дата разбора:** 2026-11-03
- **Вердикт:** отклонить (для T2 — только список кандидатов правил)

## Что делает

Стандартный набор OCA: `oca/maintainer-tools@f9b919b` (генерация README, `website` в манифесте, внешние зависимости),
`OCA/odoo-pre-commit-hooks@v0.1.6` (XML/PO/CSV-проверки), prettier 3.6.2 + plugin-xml, eslint 9.35, ruff v0.13
(`py310`, isort с секциями `odoo`/`odoo.addons`, mccabe 16), pylint-odoo v9.3.15 в двух режимах: широкий
`.pylintrc` с `--exit-zero` и обязательный `.pylintrc-mandatory`.

## Что ловит / не ловит на 19.0

- Своих правил нет. Версия зашита в `16.0` (`.pylintrc:10`, `.pylintrc-mandatory:10`, `.pre-commit-config.yaml:39`).
- OCA hooks v0.1.6 (список проверок из исходников тега `3f66e31`): `xml-deprecated-oe-chatter` (только при версии
  модуля ≥ 18), `xml-deprecated-tree-attribute` (атрибуты `<tree>`, а не сам тег), `xml-deprecated-qweb-directive`,
  дубли id/полей, опасные `replace` в xpath. **Не ловит** `attrs`/`states`, `<tree>`, `type='json'`,
  `_sql_constraints`, `read_group`, `res.partner.mobile/title`, `groups_id`, `hr.contract`.
- pylint-odoo: `deprecated-name-get`, `deprecated-odoo-model-method`, `attribute-deprecated`, `sql-injection`,
  `invalid-commit`, `except-pass`, `translation-*`, `external-request-timeout`. Перечень устаревших методов в v9.3.15
  не проверен.
- `valid-odoo-versions=16.0` в обязательном гейте → на манифестах `19.0.*` ожидается падение `manifest-version-format`
  (вывод из конфигурации; не запускали).
- Побочный эффект: `oca-fix-manifest-website` с аргументом `https://github.com/focuz-ai/odoo-spec-kit` перепишет
  `website` в манифестах проекта.

## Сравнение с T2 (`boost:odoo19-lint`)

T2 — ровно то, чего тут нет: правила версионных ловушек 19.0 с цитатой из исходников. Кит подтверждает, что
стандартные OCA-инструменты эти ловушки не закрывают, так что T2 не дублирует pylint-odoo.

Кандидаты правил сверх плана T2 (сверены с `odoo@19.0`, см. `../notes.md`): `read_group(`, `hr.contract`,
`SavepointCase`, `div class="oe_chatter"`, JS `useService("rpc")`, `useService("user")`,
`registry.category("fields").add(<Класс>)`, импорт `@web/../tests/helpers/`, `/xmlrpc`·`/jsonrpc` в интеграциях
(warn, удаление в 22), префикс `version` манифеста ≠ целевая версия. В сообщениях правил можно ссылаться на
официальный `odoo-bin upgrade_code` (`odoo/upgrade_code/17.5-01-tree-to-list.py`, `18.1-00-sql-constraint.py`,
`18.1-02-route-jsonrpc.py`; LGPL-3, только идея).

Что можно разрешить разработчикам отдельно от T2: сам pylint-odoo/ruff с конфигом **под 19.0** — общий стиль и
`sql-injection`; это вне задач boost, решение пользователя.
