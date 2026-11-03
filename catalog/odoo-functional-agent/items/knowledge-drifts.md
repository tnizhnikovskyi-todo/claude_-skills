# Справочник `knowledge/20.0` и `odoo-explain`

- **Источник:** `knowledge/README.md`, `knowledge/20.0/**`, `skills/odoo-explain/SKILL.md` @ `084b690`
- **Вердикт:** формат статьи — идея; список дрейфов — вход для 20.0 после пересверки

## Что делает

42 статьи в 5 областях (`sales_crm`, `purchase_inventory`, `accounting`,
`multi_company`, `l10n_mx`). Фронт-маттер: `source` (URL доков или `путь@20.0`),
`verified_on`, `verified_against: [source|docs|live]` (32 из 42 — `source, live`),
`modules/models/settings` для grep. Обязательные разделы: When to use (правила
«если бизнес делает X — настрой Y, потому что Z»), Configuration, How to verify
(поле, которое надо прочитать назад), Pitfalls, Alternatives. `ofa stale`
находит статьи старше последнего коммита checkout'а. `odoo-explain` отвечает
только по справочнику, иначе «The compendium has no entry» и пометка **uncited**.

## Список «Known 20.0 drifts» — сверено по `odoo/odoo`

| Дрейф | 19.0 @ `e0b25b7` | 20.0 @ `b9823b8` | Верно |
|---|---|---|---|
| `get_param`/`set_param` → `get_str`/`set_str` | `ir_config_parameter.py:60,82` | `:78,124` | да |
| `ir.model.access` + `ir.rule` → `ir.access` | `ir_model.py:2095`, `ir_rule.py:16` | `ir_access.py:64-66` | да |
| Курс: `<=` → `<` дата | `res_currency.py:127` | `:186` | да |
| `ir.attachment.datas` удалено | `ir_attachment.py:473` | только `raw` `:618` | да |
| `product.template.store_by` | нет | `addons/stock/models/product.py:837` | да |
| `stock.move.product_uom` → `uom_id` | `stock_move.py:67` | `:68` | да |
| `purchase.order.line.product_uom_id` → `uom_id` | `:43` | `:49` | да |
| `res.users.group_ids` (уже в 19.0) | `res_users.py:257` | `:250` | да |
| `account.tax.fiscal_position_ids` (уже в 19.0) | `account_tax.py:95,101` | — | да (19.0) |

Остальные пункты (`require_payment`, `base_vat`, inter-company поля, авто-план
`mx`) не сверяли.

## Что берём

- Формат статьи с `verified_against` и обязательным «How to verify» — как идея для
  наших справок (T1).
- Список дрейфов — готовый чек-лист для будущей ветки 20.0 `source-check`/линтера;
  в нашу справку — только с собственной ссылкой `файл:строка`.
- Сам справочник не берём: 20.0, акцент на мексиканской локализации.

## Атрибуция

Факты, перепроверенные по `odoo/odoo` (LGPL-3); идея формата — xmglord/odoo-functional-agent
@ `084b690`, MIT.
