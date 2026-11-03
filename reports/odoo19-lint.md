# Отчёт: T2 `odoo19-lint`

Ветка `build/odoo19-lint`. Задача T2 из `roadmap.md` («Третий проход»):
барьер на главную слабость модели — факты Odoo 19 (`synthesis.md` п. 3).
Основа: идеи из `catalog/odoo-agent-pro-kit/` (линтер `checks/odoo_lint.py`,
Apache-2.0 — только идея), `catalog/odoo-lens/` (без лицензии — только
идеи), сверенные факты из `catalog/unclecatvn-skills/`,
`catalog/mart337i-odoo-skills/`, `catalog/dooservice-odoo-skills/`, и
F2–F5. Код и тексты свои.

## Что сделано и где

| Путь | Что |
|---|---|
| `plugins/boost/skills/odoo19-lint/SKILL.md` (~100 строк) | Триггер: после записи/правки файлов модуля Odoo 19 и до «готово»/ревью/коммита, либо «проверь на ловушки 19». Не для Odoo ≤ 18, вопросов без кода и не-Odoo. Шаги: скрипт (если есть Bash) или сверка по таблице/`references/rules.md` (если нет); как читать ERROR/WARN; повторная проверка; формат строки итога; «0 находок ≠ установится» |
| `plugins/boost/skills/odoo19-lint/scripts/odoo19_lint.py` (~600 строк, stdlib) | 23 правила. Python — `ast` (код не импортируется), XML — `expat` со строками, CSV — `csv` (модель по имени файла), манифест — `ast.literal_eval`. Учитывает поля, которые модуль сам добавляет (`mobile` в своём `res.partner` — не ошибка), любые Many2one на `res.partner` (`driver_id.mobile`), подавление `odoo19-lint: ignore`. `--json`, `--rules`; выход 1 при ERROR |
| `plugins/boost/skills/odoo19-lint/references/rules.md` | Все правила для режима без Bash: что, почему, как исправить, источник `odoo/odoo@19.0:путь:строки`, Grep-рецепт |
| `plugins/boost/skills/odoo19-lint/references/attribution.md` | Откуда идеи, лицензии, что проверено и не включено, контроль ложных срабатываний |
| `plugins/boost/evals/odoo19-lint/test_odoo19_lint.py` | 11 unittest: позитив на каждое правило (`tests/bad/`), ноль находок на правильном коде 19 (`tests/good/`), подавление, поле модуля, пилот (K9), ключ eval-фикстуры |
| `plugins/boost/evals/odoo19-lint/tests/{bad,good}/td_lint/` | Один и тот же модуль: с ловушками и правильно для 19 |
| `plugins/boost/evals/odoo19-lint/_fixture/addons/td_rental/` | Модуль для кейса ревью: 7 ловушек ERROR + 2 WARN среди правильного кода 19 |
| `plugins/boost/evals/odoo19-lint/{review-module,write-module,odoo16-negative}/` | 3 eval-кейса |

```bash
python3 -I -m unittest discover -s plugins/boost/evals/odoo19-lint -p 'test_*.py'   # 11 OK
python3 -I plugins/boost/skills/odoo19-lint/scripts/odoo19_lint.py <модуль>
claude plugin validate plugins/boost                                               # passed
```

## Правила и источники

Все строки сверены по `odoo/odoo` ветки `19.0`, коммит `e0b25b7`
(sparse-клон в scratchpad, код Odoo не запускался).

| Правило | Уровень | Что ловит | Источник `odoo/odoo@19.0:` |
|---|---|---|---|
| `view-tree` | ERROR | `<tree>`, xpath `//tree`, `…/tree` | `odoo/addons/base/models/ir_ui_view.py:149-156`, `:610-617` |
| `view-mode-tree` | ERROR | `view_mode` с `tree`, `(False, 'tree')` | `odoo/addons/base/models/ir_actions.py:318`, `:401-408`; `ir_ui_view.py:3054-3058` |
| `tree-view-ref` | WARN | контекст `tree_view_ref` | `ir_ui_view.py:3024-3026` |
| `view-attrs-states` | ERROR | `attrs=`, `states=`, `<attribute name="attrs">` | `ir_ui_view.py:495-499` |
| `route-type-json` | WARN | `@route(type='json')` | `odoo/http.py:812-818` |
| `sql-constraints` | ERROR | `_sql_constraints` (игнорируется) | `odoo/orm/model_classes.py:159-164` |
| `partner-mobile-title` | ERROR | `res.partner.mobile/title` в related, depends, коде, вью, xpath | `odoo/addons/base/models/res_partner.py:184-313` (+ ни один `addons/*/models/*.py` не добавляет) |
| `groups-fields` | ERROR | `res.groups.users/category_id`, `groups_id` у `res.users`, `ir.ui.menu`, `ir.actions.*`, `ir.ui.view` (XML, Python, CSV) | `res_groups.py:17,36`; `res_groups_privilege.py:13`; `res_users.py:257`; `ir_ui_menu.py:29`; `ir_actions.py:329,661`; `ir_actions_report.py:183`; `ir_ui_view.py:175` |
| `inherit-list-no-name` / `-implicit-name` | ERROR / WARN | `_inherit = [...]` без `_name`: новая модель (или совпадение имени класса) | `odoo/orm/models.py:241-249` |
| `cron-numbercall` | ERROR | `ir.cron` `numbercall`, `doall` | `ir_cron.py:99-122` |
| `name-get` | ERROR | `def name_get`, `.name_get()` | `odoo/orm/models.py:1438`; `name_get` в `odoo/` нет |
| `read-group` | WARN | `read_group()` | `odoo/orm/models.py:2754-2755` |
| `private-env` | WARN | `self._context/_cr/_uid` | `odoo/orm/models.py:5930-5943` |
| `toggle-active` | WARN | `toggle_active()` | `odoo/orm/models.py:5807-5813` |
| `notify-progress` | WARN | `_notify_progress()` | `ir_cron.py:823-824`, `:846` |
| `api-returns` | ERROR | `@api.returns` | `odoo/api/__init__.py:5-17` |
| `user-has-groups` | ERROR | `user_has_groups()` | `res_users.py:1034,1066` |
| `group-operator` | WARN | `group_operator=` | `odoo/orm/fields.py:485-487` |
| `product-type` | ERROR | `detailed_type`, `type='product'` | `addons/product/models/product_template.py:58-65`; `addons/stock/models/product.py:834` |
| `uom-fields` | ERROR | `uom.uom` `category_id/uom_type/factor_inv` | `addons/uom/models/uom_uom.py:34-44` |
| `line-product-uom` | ERROR | `product_uom` у `sale/purchase.order.line` (не `stock.move`) | `addons/sale/models/sale_order_line.py:132`; `addons/purchase/models/purchase_order_line.py:43`; `addons/stock/models/stock_move.py:67` |
| `manifest-hook-path` | ERROR | хук манифеста путём с точкой | `odoo/modules/loading.py:182-185` |

Не включено: `<group expand>` в поиске (правило кита) — по RNG 19.0 не
подтвердил однозначно.

## Проверка скрипта

- **unittest:** 11 тестов, все проходят. На `bad/` найдено ровно ожидаемое
  (по позитиву на каждое правило, тест сверяет множество целиком, лишних
  нет), на `good/` — 0 находок.
- **Ложные срабатывания на самом Odoo 19.0:** `addons/*/{models,views,data,
  security,controllers,wizard}`, `__manifest__.py`, `odoo/addons/base` —
  8962 файла: **0 ERROR, 1 WARN** (настоящий `self.read_group` в
  `addons/l10n_dk/models/account_account.py:22`). По ходу так нашлись и
  убраны два ложных срабатывания: `move.product_uom` (у `stock.move` поле
  осталось) и ключ `'product_uom'` в vals для `stock.move`.
- **Пилот `pilot/addons` (K9):** ровно 1 находка —
  `partner-mobile-title td_workshop/models/workshop_order.py:17`
  (`related="partner_id.mobile"`), это K9 из `pilot-notes/KEYS.md`. Ловушки
  «не ошибки» из ключа (`models.Constraint`, `<list>`, `invisible=`,
  `<chatter/>`) не задеты. Остальные K* — не версионные, вне задачи линтера.

## A/B

Судья sonnet, `--runs 3`, `-j 4`, `--allow-tools Write Edit`. Bash в eval
закрыт (нет песочницы), поэтому во всех прогонах скилл работал **без
скрипта**, по таблице `SKILL.md` и `references/rules.md`. Ни один прогон
не упёрся в лимит стоимости (`partial: false`, платные грейдеры не
пропускались).

### Кейсы скилла (`--case 'odoo19-lint/*' --scaffold`, $2.32 за оба плеча)

| Кейс | С плагином | Без | Δ | Что решило |
|---|---|---|---|---|
| `review-module` (ревью модуля 19, 7 ловушек среди правильного кода) | **1.00** (3/3) | 0.25 (0/3) | **+0.75** | без скилла ни в одном прогоне не названы все 4 «трудные» (`customer_id.mobile`, `_inherit` списком без `_name`, `res.groups category_id/users`, `numbercall`); в 1 из 3 — ложная находка на правильном коде 19 |
| `write-module` (новый модуль 19 с нуля) | **1.00** (3/3) | 0.84 (0/3) | **+0.16** | без скилла 3/3 пишут `related='customer_id.mobile'`/`.title`; остальное база знает |
| `odoo16-negative` (правка вью в модуле 16) | 1.00 | 1.00 | 0 | скилл не сработал (3/3), синтаксис 16 (`attrs`/`states`) сохранён |
| **Среднее** | **1.00** | 0.70 | **+0.30** | |

Стоимость ответа с плагином выше на 25–30% (review $0.26 против $0.21 за
прогон, write $0.11 против $0.09): чтение таблицы и `rules.md`.

### Главная метрика: `general --tag hard` ($1.41 за оба плеча)

| Кейс | С плагином (0.5.0-dev, с `odoo19-lint`) | Без плагина | Плагин **без** `odoo19-lint` (копия, `--ablation none`, $0.78) |
|---|---|---|---|
| `odoo19-api-traps` | **1.00** (1/1/1) | 0.77 | 0.76 |
| `odoo19-sales-traps` | **1.00** (1/1/1) | 0.74 | 0.74 |
| **Среднее** | **1.00** | 0.755 | 0.747 |

- **Δ = +0.245**, база совпала с прошлой (0.755, `reports/foundation.md`).
- Весь прирост даёт `odoo19-lint`: копия плагина без него не лучше базы
  (там срабатывает только `lean-change`, `source-check` на задачах записи
  кода не вызывается).
- Без скилла стабильно падают ровно те грейдеры, ради которых он сделан:
  `py-installable` (`driver_id.mobile` / `groups_id` / `.users`),
  `py-no-mobile`, `py-no-title`.
- В trace (повтор с `--keep-temp`, 1 прогон на кейс, $0.23) скилл
  вызывается **до** записи файлов, как справка, а не после, как задумано
  в `SKILL.md`. Результат тот же; хук после записи (ниже) сделал бы
  проверку обязательной.

Итого потрачено на прогоны: **$4.74** ($2.32 + $1.41 + $0.78 + $0.23).

## Что не получилось / ограничения

- **Скрипт в eval не исполнялся**: Bash в облачном eval закрыт. Скрипт
  проверен unittest'ами, на пилоте и на 8962 файлах самого Odoo 19, но
  прирост в A/B дала таблица в `SKILL.md`. Это значит, что большая часть
  пользы — в компактном списке фактов 19 с источниками; скрипт нужен для
  ревью больших модулей и для хука.
- Скрипт видит только переданные пути: поле, которое добавляет другой
  аддон (или enterprise), даст ложное срабатывание — подавляется
  `odoo19-lint: ignore`.
- `line-product-uom`, `partner-mobile-title` в Python — эвристика по имени
  поля/переменной (`*partner*`, Many2one на `res.partner` из сканируемого
  кода, `line`/`order_line`); `driver_id` ядра, например у
  `fleet.vehicle`, без сканирования ядра не распознаётся.
- Регрессионный уровень `general` (14 кейсов) не прогонялся (бюджет).
  Риск: триггер «после правки модуля Odoo 19» сработает на
  `odoo19-port`/`odoo19-constraint` — ожидаемо в плюс, но не измерено.

## Хук (только предложение)

`plugins/boost/hooks/` занят `cloud-memory`, поэтому хук не добавлен.
Предложение для главной сессии:

- `PostToolUse` на `Write|Edit` (matcher по пути `*.py|*.xml|*.csv`
  внутри каталога с `__manifest__.py`, где `'version'` начинается с
  `19.0`): `python3 -I ${CLAUDE_PLUGIN_ROOT}/skills/odoo19-lint/scripts/odoo19_lint.py <файл>`;
- только **предупреждение** (exit 0, вывод в `additionalContext`), без
  блокировки; молчит, если файл не из модуля 19 или находок нет;
- время: один файл — десятки мс (весь Odoo 19, 8962 файла, — несколько
  секунд), без сети.

Стоит сделать, если повторные прогоны покажут, что модель не вызывает скилл
сама в обычной работе (в eval вызывала 6 из 6 раз на задачах 19).

## Нужные правки общих файлов (для главной сессии)

1. `plugins/boost/README.md`, таблица «Состав»: строка
   `| odoo19-lint | Барьер на ловушки Odoo 19: 23 правила с цитатой odoo/odoo@19.0 (вью tree/attrs, view_mode, _sql_constraints, res.partner.mobile/title, поля групп, _inherit списком без _name, numbercall, name_get, read_group, self._context, uom, товар, product_uom…); stdlib-скрипт odoo19_lint.py и таблица для работы без Bash | +0.30 на 3 кейсах (+0.75 ревью); general/hard 0.755 → 1.00 | T2 |`.
2. `plugins/boost/.claude-plugin/plugin.json`: `version` → `0.5.0`, в
   `description` добавить «проверка ловушек Odoo 19».
3. `roadmap.md`: T2 → готово (ссылка на этот отчёт); F5 — у нас есть
   правило `inherit-list-no-name` с тем же источником
   (`odoo/orm/models.py:241-249`), его можно использовать в T4
   (`odoo-model-map`).
4. `PROVENANCE.md`, раздел `boost`: `| odoo19-lint (+ odoo19_lint.py) | infovpcs/odoo-agent-pro-kit @ 99515db, plugin/hooks/checks/odoo_lint.py; ChengyanOo/odoo-lens @ 2482f92; факты — odoo/odoo@19.0 e0b25b7 | Apache-2.0; нет лицензии; LGPL-3 (факты) | идея (код и текст свои) | plugins/boost/skills/odoo19-lint/references/attribution.md |`.
5. `synthesis.md` п. 3: «справка в контексте поднимает 0.755 → 1.00»
   теперь подтверждено и скиллом: `odoo19-lint` даёт 1.00 на `hard`
   (без него плагин 0.747). Приоритет Context7/`source-check` для этой
   слабости можно снизить; T1 (таблица фактов в `source-check`) стоит
   брать из `references/rules.md`, чтобы не держать два списка.
6. `plugins/boost/evals/general/README.md`: строка про плагин на `hard`
   (1.00 с `odoo19-lint`).
7. Опционально: хук (раздел выше) в `plugins/boost/hooks/` рядом с
   хуками `cloud-memory`.

## Открытые вопросы

- Прогнать регрессионный `general` (~$5) с новым скиллом.
- Хук или только скилл: решить после использования в реальной работе.
- Enterprise-аддоны (могут добавлять поля в `res.partner`) не проверены —
  исходников нет.
