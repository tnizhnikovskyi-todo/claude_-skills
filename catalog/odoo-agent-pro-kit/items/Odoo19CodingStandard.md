# `Odoo19CodingStandard` (и `OdooTools19`, `Odoo19ExistingDependencyContext`)

- **Тип:** скиллы
- **Источник:** `plugin/skills/Odoo19CodingStandard/SKILL.md` (443 строки), `OdooTools19` (39), `Odoo19ExistingDependencyContext` (58)
- **Вердикт:** адаптировать выборочно (проверенные факты → наши `references/`)

## Что делает

Справочник правил Odoo 19: виды, `models.Constraint`, `env.context`, роуты,
`Markup` в `message_post`, новая модель групп (`res.groups.privilege`), поиск
без `<group expand>`, `ir.cron` без `numbercall`, `compute_sql` (только 19.3+),
`NewId` в compute счётчиков (`counts.get(rec.id, 0)`), большой раздел о
параметрах `@route` (`auth='bearer'`, `readonly=True`, `save_session=False`,
`handle_params_access_error`), RNG-схема XML-данных, тёмная тема сайта.

## Точность (сверка с 19.0, детали в `../notes.md`)

- Верно: `privilege_id`/`user_ids`, `<group>` без `expand`/`string`,
  `jsonrpc` (с 19.0), `ir.cron`, `allow_none=False` у XML-RPC, `compute_sql` нет в 19.0,
  параметры `readonly`/`bearer`/`handle_params_access_error` есть в `http.py` 19.0.
- Ошибка: пример `<act_window>` и `view_mode="tree,form"` в разделе «RNG» — в
  `import_xml.rng` 19.0 элемента нет.
- `OdooTools19`: раздел «Copilot Agent Integration (v4.0+)» ссылается на
  несуществующие файлы и модели `gpt-4o`/`claude-3-5-sonnet` — мусор.
- Раздел про тёмную тему сайта (~60 строк CSS) — частный проект автора, грузится всегда вместе со скиллом.

## Сравнение с нашим

- `boost:lean-change` + `references/odoo19.md` уже покрывают `Constraint`, `list`,
  атрибуты вместо `attrs`, стандартные механизмы до кода. Не покрывают: группы
  (`privilege_id`), поиск без `expand`, `jsonrpc`, параметры `@route`, `NewId`.
- `boost:source-check` даёт метод (источник → цитата), но не список ловушек.
- `odoo19-mvp-build:code-dev` построчно сравнить не удалось (текст недоступен в контейнере).

## Оценка

| Критерий | Балл | Комментарий |
|---|---|---|
| Прирост | 1 | Часть фактов новая для нас, но есть ошибки; без A/B |
| Частота | 2 | |
| Надёжность | 1 | Смесь проверенного, устаревшего и выдуманного |
| Стоимость контекста | 1 | 443 строки целиком, без `references/` |
| Безопасность | 3 | Только текст |
| Поддержка | 2 | |
| **Итого** | **10/18** | |

## Что взять

В `plugins/boost/skills/lean-change/references/odoo19.md` (или в `source-check/references/`)
таблица «ловушка → правильно → источник 19.0» из проверенных пунктов: группы,
`<group>` в поиске, `jsonrpc`, `_sql_constraints` игнорируется, `ir.cron`, `NewId`+`.get()`,
чек-лист ревью роута (auth / methods / csrf / save_session / readonly / sitemap). Текст писать
свой, факты с цитатой из исходника.

Источник, куда и как (лицензия Apache-2.0, SHA `99515dbc3526e6877cccb5f8a0de3b7bd1050574`): см. таблицу «Что и куда перенести» в [`../README.md`](../README.md).
