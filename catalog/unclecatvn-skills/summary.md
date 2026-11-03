# unclecatvn-skills: сводка

- **Что это:** плагин для Odoo 16–19 (MIT, 1.0.20, активный: 109 коммитов
  с января 2026, CI, 5 авторов): справочные паки по версиям, скилл
  `odoo-workflow` с read-only хелпером `odoo_trace.py`, агенты ревью и
  трассировки, `odoo-commit`, `dtg-base`.
- **Гипотеза** «документация Odoo в виде скиллов» верна наполовину: главное —
  метод «нет цитаты `file:line` из реальных исходников — нет кода».
- **Точность 19.0:** 11 из 11 проверенных утверждений пака совпали с
  `odoo/odoo@19.0` (`_sql_constraints`, `models.Constraint/Index`,
  `read_group`, `@api.returns`, `_cr`, правила `_name`, демо, `jsonrpc`,
  `privilege_id`, `aggregator`). **Но** пака не хватает именно на нашей
  боли: нет удаления `res.partner.mobile`/`title` и `groups_id` → `group_ids`.
  Эти ошибки ловит не текст, а хелпер по исходникам.
- **Безопасность:** хелпер — stdlib, только чтение, без сети; хуков и MCP
  нет. Минусы: триггер «Mandatory … ANY Odoo change», ~2× токенов,
  `odoo-commit` запрещает AI-атрибуцию.
- **Вердикт:** **адаптировать**, 13/18. Плагин не ставить.
- **Взять** (источники `путь@SHA`, способ и лицензия — таблица «Что взять» в `README.md`; всё MIT): (1) `api-highlights.md` 19.0 + наши дополнения с `file:line` в
  `boost:source-check/references/`; (2) формат Context Brief и правило
  «сломанный grep ≠ NOT FOUND» в `source-check` и предложение для
  `code-dev`; (3) рецепт sparse-клона `odoo/odoo@19.0` в облаке как
  источник уровнем выше документации; (4) `odoo_trace.py` как движок
  `field/xmlid/method` после прогона и A/B; (5) ловушки DoD (`of 0 tests`,
  версия миграции) в `testing`; (6) правила `sudo` в `security-review`.
- **Открыто:** разрешение запустить `odoo_trace.py` на клоне 19.0;
  текст `code-dev` для сравнения (в сессии его нет).
