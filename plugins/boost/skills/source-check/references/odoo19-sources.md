# Официальные источники Odoo 19

Адреса проверены 2026-11-02 (HTTP 200). Если страница переехала — ищи
на `odoo.com/documentation/19.0/`, не подставляй другую версию.

## Документация (`https://www.odoo.com/documentation/19.0/...`)

| Тема | Путь |
|---|---|
| ORM: модели, поля, декораторы, `Constraint`/`Index`, recordsets, домены | `developer/reference/backend/orm.html` |
| Права: `ir.model.access`, record rules, группы | `developer/reference/backend/security.html` |
| Действия (window, server, cron, отчёты) | `developer/reference/backend/actions.html` |
| XML/CSV-данные модуля | `developer/reference/backend/data.html` |
| Манифест модуля | `developer/reference/backend/module.html` |
| Тесты | `developer/reference/backend/testing.html` |
| HTTP-контроллеры | `developer/reference/backend/http.html` |
| QWeb-отчёты | `developer/reference/backend/reports.html` |
| Производительность | `developer/reference/backend/performance.html` |
| Архитектура вью (list, form, kanban…) | `developer/reference/user_interface/view_architectures.html` |
| Записи `ir.ui.view`, наследование вью | `developer/reference/user_interface/view_records.html` |
| OWL-компоненты | `developer/reference/frontend/owl_components.html` |
| External API (XML-RPC/JSON-RPC) | `developer/reference/external_api.html` |
| Скрипты миграции | `developer/reference/upgrades/upgrade_scripts.html` |
| Release notes 19 | `https://www.odoo.com/odoo-19-release-notes` |

Пользовательская документация (функциональность, настройки):
`https://www.odoo.com/documentation/19.0/applications/...`.

## Исходники ветки 19.0

Читать через `https://raw.githubusercontent.com/odoo/odoo/19.0/<путь>`,
цитировать как `https://github.com/odoo/odoo/blob/19.0/<путь>#L<строка>`.

| Что | Путь |
|---|---|
| `BaseModel`, CRUD, `_rec_names_search`, `name_search` | `odoo/orm/models.py` |
| Обработка атрибутов модели (что больше не поддерживается) | `odoo/orm/model_classes.py` |
| `Constraint`, `Index`, `UniqueIndex` | `odoo/orm/table_objects.py` |
| Базовый `Field`, параметры полей | `odoo/orm/fields.py` |
| Many2one / One2many / Many2many | `odoo/orm/fields_relational.py` |
| Числовые / текстовые / даты / selection | `odoo/orm/fields_numeric.py`, `fields_textual.py`, `fields_temporal.py`, `fields_selection.py` |
| Декораторы `api.*` | `odoo/orm/decorators.py` (реэкспорт в `odoo/api/__init__.py`) |
| Environment | `odoo/orm/environments.py` |
| Домены | `odoo/orm/domains.py` |
| Record rules, вью, действия, пользователи | `odoo/addons/base/models/ir_rule.py`, `ir_ui_view.py`, `ir_actions.py`, `res_users.py` |
| Модули приложений | `addons/<модуль>/models/*.py` |

Внимание: в 19.0 ORM разнесён по `odoo/orm/`; путь `odoo/models.py` в этой
ветке не существует (404). Не переноси пути из 16/17 по памяти.

## Context7

`libraryId: /websites/odoo/19.0` — фрагменты с `odoo.com/documentation/19.0`.
В ответе Context7 есть ссылка на исходную страницу: цитируй её, а не Context7.
