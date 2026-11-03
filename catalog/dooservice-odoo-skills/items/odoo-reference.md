# odoo-reference (19.0)

- **Тип:** скилл-справочник (688 файлов, 4 МБ на версию), генерируется `tools/build_reference.py`
- **Источник:** своё у dooservice, из исходников `odoo/odoo@19.0` (Community)
- **Вердикт:** взять как справочник через их плагин (по желанию); идея → `odoo-model-map`

## Что делает

- `addons.md`: по строке на аддон: какие модели определяет и какие расширяет.
- `models/<addon>.md`: поля (тип, comodel, label, флаги, `related`, `compute`),
  публичные методы, точки расширения (`_prepare_*`, `_get_*`, `_action_*` …).
- `xmlids/<addon>.md`: XML id по моделям записи; для вью указано `on <model>` и
  `inherits <view>`.
- `settings.md`: каждое поле `res.config.settings` и как оно хранится (поле
  компании, `parameter`, `group`, `installs`, computed).
- В `SKILL.md` готовые grep-рецепты; читать целиком запрещено.

По README сверено с реестром работающей Odoo каждой версии
(`tools/reference/check.py`): расхождений нет. Мы проверили выборочно: поля
`account.tax.fiscal_position_ids/original_tax_ids` в `models/account.md:962-963`
совпадают с `account_tax.py:95,101`.

## Сравнение с `boost:odoo-model-map`

| | odoo-model-map | odoo-reference |
|---|---|---|
| Что видит | код проекта и любые аддоны на диске | только стандарт Community 19.0 |
| Нужен checkout | да | нет, справочник готов |
| Связи `_inherit`, вью, права проекта | да | нет |
| Settings → как хранится | нет | да |
| Enterprise | если есть на диске | нет |

Дополняют друг друга. В облачной сессии без исходников Odoo справочник даёт имена
стандарта сразу.

## Перенос

- В `odoo-model-map` строка «стандартные имена без checkout-а — в
  odoo-reference, если плагин установлен; иначе sparse-checkout `odoo/odoo@19.0`»
  (рецепт sparse-checkout мы обкатали в этом разборе: см. `../notes.md`).
- Свой генератор не пишем: LGPL и стоимость поддержки. Берём их плагин с пином коммита.
