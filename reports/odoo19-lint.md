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

## Второй круг (2026-11-03, по запросу главной сессии)

В ветку смёрджен хаб `claude/admiring-cannon-25jueb` (`900249f`). На момент
работы в хабе не было ни нашей ветки, ни трёх новых разборов. Разборы
прочитаны из `analysis/panus-odoo-dev-skill`, `analysis/odoo-migrate-to-20`
и `analysis/odoo-spec-kit`.

### Новые правила (все 17 подтверждены; сверено с 19.0 `e0b25b7` и 18.0 `f0ef96d`)

| Правило | Уровень | Что | Источник `odoo/odoo@19.0:` (и было в 18.0) |
|---|---|---|---|
| `api-model-create` | ERROR | `@api.model` + `create(self, vals)` получает список | `odoo/orm/decorators.py:322-323, 364-369` |
| `old-constraints` | ERROR | `_constraints` игнорируется | `odoo/orm/model_classes.py:159-161` |
| `fields-date-alias` | ERROR | `fields.date/datetime` | `odoo/fields/__init__.py:5-22` (18.0 `odoo/fields.py:8`) |
| `models-newid` | ERROR | `models.NewId` | `odoo/models/__init__.py:7-30`, `odoo/api/__init__.py:4` (18.0 `odoo/models.py:56`) |
| `odoo-registry` | ERROR | `odoo.registry()` | `odoo/init.py:33-43` (18.0 `odoo/__init__.py:30-41`, deprecated) |
| `savepoint-case` | ERROR | `SavepointCase` | `odoo/tests/common.py:990,1186` (нет и в 18.0) |
| `search-group-attrs` | ERROR | `<group expand/string>` в `<search>` | `odoo/addons/base/rng/common.rng:295-313` (в 18.0 были), `ir_ui_view.py:509-515` |
| `digits-uom` | ERROR (молча) | `digits='Product Unit of Measure'` | `addons/uom/data/uom_data.xml:5-8`, `decimal_precision.py:23-27` (18.0 `product_data.xml:36`) |
| `default-user` | ERROR | `base.default_user` | `base_groups.xml:114`, `res_users.py:209` (18.0 `res_users_data.xml:31`) |
| `login-classmethod` | ERROR | `_login(cls, db, …)` | `res_users.py:760` (18.0 `:924-925`) |
| `default-get-kwarg` | ERROR | `default_get(fields_list=…)` | `odoo/orm/models.py:1271` (18.0 `odoo/models.py:1639`) |
| `line-tax-ids` | ERROR | `sale.order.line.tax_id`, `purchase.order.line.taxes_id` | `sale_order_line.py:162`, `purchase_order_line.py:34` (18.0 `:159`, `:33`) |
| `removed-module` | ERROR | `depends` на 46 аддонов 18.0, которых нет в 19.0 (`web_editor`, `hr_contract`, `membership`, `website_jitsi`…) | `odoo/modules/module_graph.py:257-269`; список по `git ls-tree addons/` |
| `oe-chatter` | ERROR (молча) | `<div class="oe_chatter">` | `addons/mail/static/src/chatter/web/form_compiler.js:46-48` |
| `osv-expression` | WARN | `odoo.osv.expression` | `odoo/osv/__init__.py:4` |
| `js-use-service` | ERROR | `useService("rpc"/"user")` | `addons/web/static/src/core/utils/hooks.js:142-147`, `network/rpc.js:93`, `user.js:254` |
| `manifest-version` | ERROR (молча) | версия из 4–5 частей не с `19.0.` → `installable=False` | `odoo/modules/module.py:465-467, 550-566` |

Расхождения с подсказками:

- `default_get(fields_list)` как переопределение не ломается, потому что
  позиционный вызов работает. Правило ловит только вызов с именем
  `fields_list=`.
- `SavepointCase` убрали раньше 18.0, но в 19.0 это всё равно ловушка.
- `oe_chatter` и в 18.0 уже не компилировался. Правило оставлено, потому
  что поломка молчаливая.
- `<group expand>` в первом круге я не включил, потому что смотрел только
  в `search_view.rng`. Во втором круге подтвердил по `common.rng`.

Всего правил стало 40 (ERROR 31, WARN 9).

### Официальные кодмоды

Для правил, у которых в 19.0 есть автозамена, скрипт печатает строку
«автозамена: `odoo-bin upgrade_code --script <имя> --dry-run`». Сам
механизм описан в `odoo/cli/upgrade_code.py:168-174`.

| Правило | Кодмод |
|---|---|
| `view-tree`, `view-mode-tree` | `17.5-01-tree-to-list` |
| `sql-constraints` | `18.1-00-sql-constraint` |
| `route-type-json` | `18.1-02-route-jsonrpc` |
| `private-env` | `18.5-00-deprecated-properties` |

Код кодмодов не брал, только ссылки. В `SKILL.md` записано, что запускать
кодмод можно только с согласия пользователя.

### Справочники (урок darwin-skill)

- Файлы `*.md` скрипт не читал и раньше. Это касается `rules.md`,
  `SKILL.md` и `odoo-version-notes.md` из маркетплейса.
- Но строки в любом `.py` он проверял. На каталоге `plugins/boost/skills`
  нашлось **8 ложных находок в самом `odoo19_lint.py`**: его
  сообщения-примеры.
- Исправление: по умолчанию проверяются только файлы внутри модуля Odoo,
  то есть с `__manifest__.py` выше по дереву. Остальное пропускается со
  счётчиком «вне модулей», флаг `--all-files` снимает ограничение.
- Тесты `ReferenceFiles` проверяют три вещи: 0 находок на
  `plugins/boost/skills`, ни один `.md` не читается, и с `--all-files`
  собственный скрипт снова виден (то есть исключение действительно нужно).
- Хук из предложения этим ограничением тоже защищён.

### Проверка

- **unittest:** 14 тестов, все проходят.
  - Позитив на каждое из 40 правил лежит в `tests/bad/`, новые файлы:
    `models/round2.py`, `views/round2.xml`, `static/src/js/widget.js`,
    `tests/test_ticket.py`, плюс правки манифеста.
  - На тех же файлах в `tests/good/` 0 находок. Среди них верные
    конструкции 19, которые легко принять за ошибку: `<group string expand>`
    в `<form>`, `product.template.taxes_id`, `base.default_user_group`,
    `useService("orm")`, комментарий с `useService("rpc")`.
- **Ложные срабатывания на Odoo 19.0:** 9884 файла, вместе с JS
  `web`/`mail` и `odoo/tests` (по `--all-files`): 0 ERROR, 1 WARN, тот же
  `read_group` в `l10n_dk`.
- **Полнота на Odoo 18.0** (929 файлов sparse-клона): новые правила
  срабатывают на настоящем старом коде. Например, `_login` classmethod
  (`res_users.py:925`), `base.default_user` (`:367`), `taxes_id` и
  `Product Unit of Measure` в `purchase_order_line.py`, 29
  `removed-module` в манифестах.
- **Пилот:** по-прежнему ровно K9.

### A/B второго круга: `review-module`

В фикстуру добавлены две ловушки второго круга: `@api.model create` и
`<group expand string>` в поиске. Добавлен грейдер `round2-traps`; старые
грейдеры не менялись. Прогон: судья sonnet, `--runs 3`, лимит $4.
Потрачено **$1.82**, `partial: false`.

| Грейдер | С плагином | Без |
|---|---|---|
| `hard-traps` | 3/3 | 0/3 |
| `other-traps` | 3/3 | 1/3 |
| `round2-traps` | **3/3** | **0/3** |
| `no-false-positives` | 2/3 | 2/3 |
| **Счёт** | **0.93** | 0.20 |
| **Δ** | **+0.73** | |

Сработало в первом круге +0.75. Единственное падение в плече «с
плагином» (`no-false-positives`, голоса судьи 2:1) спорное: в ответе все
конструкции-приманки перечислены в разделе «Что проверено и в порядке».
Вероятно, ошибся судья, но это не подтверждено. Лишним пунктом могла
быть названная «логическая проблема с sequence».

Без скилла модель ни разу не назвала ни одну ловушку второго круга.
Скрипт в eval по-прежнему не исполнялся (нет Bash): прирост дала таблица
в `SKILL.md`.

### Правки общих файлов (дополнение к списку выше)

1. `plugins/boost/README.md`, строка `odoo19-lint`: «40 правил»;
   A/B второго круга — +0.73 на `review-module`.
2. `PROVENANCE.md`, строка `odoo19-lint`: добавить источники идей
   - `panusbodee-owen/odoo-dev-skill @ 76e8b87` (нет лицензии, идея);
   - `tanim913/odoo-migrate-to-20 @ a5507bf` (MIT, идея и список);
   - `focuz-ai/odoo-spec-kit @ 23df08b` (MIT, идея);
   - ссылки на `odoo/upgrade_code` (LGPL-3, только ссылка).
3. `roadmap.md` T2: второй круг готов.
4. Для T1 (`source-check`) и `odoo-version-notes.md`: единый список фактов
   19 с двумя ветками источников — `references/rules.md`, раздел «Второй
   круг».

Итого на прогоны за оба круга: **$6.56**.
