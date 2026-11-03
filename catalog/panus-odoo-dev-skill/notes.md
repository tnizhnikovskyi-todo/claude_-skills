# panus-odoo-dev-skill: рабочий журнал

## 2026-11-03

**Источник:** https://github.com/panusbodee-owen/odoo-dev-skill,
HEAD `76e8b8761ac81f3510952524b165297fea5d0324` (2026-10-15). Всего 4 коммита,
все за 2026-10-15, автор «OWen», ★2.

**Лицензия:** файла `LICENSE` нет (`find . -name 'LICENSE*'` — пусто), в README
лицензия не названа. По п. 5 `CLAUDE.md`: только идеи своими словами, код и
текст не копируем.

**Как смотрели.** Клон в scratchpad (вне нашего репо), ничего не запускали:
ни `scaffold.py`, ни `check_compat.py`. Нестандартных git-хуков в клоне нет.
Odoo для сверки: `odoo/odoo@19.0`, коммит `e0b25b7032aacb5bf711a119c40a466888e2fc16`
(2026-10-13) — тот же, что у T2. Частичный клон (`--filter=blob:none --sparse`):
`odoo/`, `addons/web/static/src/{core,legacy,module_loader.js,…}`,
`addons/product/models`, `addons/stock/models`, `addons/mail/static/src`; отдельные
файлы — через `git show HEAD:<путь>`.

### Состав (9 файлов, 555 КБ, из них 529 КБ — демо-GIF)

| Файл | Байт | Что |
|---|---|---|
| `.claude/skills/odoo-dev/SKILL.md` | 3558 | правила экономии токенов, выбор версии (по умолчанию 18), роутер на references, стандарт кода |
| `references/versions.md` | 1851 | таблица «с версии — старое — новое», 12 строк (15–19), две строки 19 помечены `(verify)` |
| `references/patterns.md` | 3793 | шаблоны модели, вью, прав, визарда, крона, отчёта, контроллера |
| `references/testing.md` | 2132 | TransactionCase, Form, тур, команды `odoo-bin` |
| `references/l10n-th.md` | 1408 | Таиланд: сумма прописью, буддийский год, Tax ID, WHT |
| `scripts/check_compat.py` | 3688 | регэкспы по версии, `файл:строка правило подсказка`, exit 1 при находках |
| `scripts/scaffold.py` | 6395 | каркас модуля под 16–19: модель, list/form, действие, меню, ACL, тест |
| `README.md`, `odoo-dev-demo.gif` | | описание, демо |

**Права/сеть/телеметрия.** Только stdlib (`argparse`, `ast`, `os`, `re`, `sys`).
Сети, subprocess, телеметрии нет. `check_compat.py` только читает;
`scaffold.py` пишет файлы в `--path/<module>` и отказывается, если папка есть.
Хуков, MCP, `settings.json` нет. Ставится копированием папки в `~/.claude/skills/`.

### Сверка правил с 19.0

В `check_compat.py` 17 регэкспов = 15 правил (у `view_mode-tree` и
`detailed_type` по два варианта). Для цели 19 активны все.

| # | Правило panus | Вердикт | Где в `odoo@19.0` (`e0b25b7`) | Есть в T2 |
|---|---|---|---|---|
| 1 | `assets-xml`: `inherit_id="web.assets_*"` | верно | шаблона с `id="assets_backend"` нет ни в одном `addons/web/views/*.xml`; бандл объявлен в `addons/web/__manifest__.py:49` → внешний id не найден | нет |
| 2 | `legacy-js`: `odoo.define(` | верно частично | `odoo.define` есть (`addons/web/static/src/module_loader.js:242`), но требует `(name, deps[], factory)` и кидает ошибку на старый вызов `odoo.define('x', function (require) {…})` (`:47-58`). Подсказка «добавь `/** @odoo-module **/`» устарела: файлы в `static/src` транспилируются и без неё (`odoo/tools/js_transpiler.py:725-727`) | нет (JS вне границы T2) |
| 3 | `attrs` | верно | `odoo/addons/base/models/ir_ui_view.py:495-499` | да (`view-attrs-states`) |
| 4 | `states-attr` (только `field`/`button`) | верно, узко | там же: `//*[@states]` — у любого элемента | да |
| 5 | `name_get` | верно | в `odoo/` 19.0 `def name_get` нет (кроме теста `test_orm`); `_compute_display_name` — `odoo/orm/models.py:1438` | да |
| 6 | `user_has_groups` | верно | в `odoo/` нет; `has_groups`/`has_group` — `odoo/addons/base/models/res_users.py:1034,1066` | да |
| 7 | `create-single`: `@api.model` + `def create` | **верно, и серьёзнее, чем у них** | `odoo/orm/decorators.py:322-323`: `@api.model` на `create` молча превращается в `model_create_multi`; обёртка (`:364-369`) передаёт в метод **список**, даже если вызвали с dict. Тело, написанное под dict (`vals.get`, `vals['x'] = …`), падает. Без предупреждения в логе | **нет — новое правило** |
| 8 | `tree-tag`: `<tree` | верно, узко | `ir_ui_view.py:149-156` (в selection нет `tree`). Не ловит xpath `//tree` | да (`view-tree`, шире) |
| 9 | `view_mode-tree` (XML, Python) | верно, узко | `odoo/addons/base/models/ir_actions.py:318,401`. Не ловит `(False, 'tree')` в `views` | да (`view-mode-tree`, шире) |
| 10 | `oe_chatter` | верно | компилятор формы ищет только `<chatter>` (`addons/mail/static/src/chatter/web/form_compiler.js:46-47`); виджетов `mail_thread`/`mail_followers` в `addons/mail/static/src` 19.0 нет (grep — 0). Старая разметка не даёт чаттера, модуль ставится — поведение молча пропадает | **нет** |
| 11 | `group_operator` | верно (WARN) | `odoo/orm/fields.py:485-487` | да |
| 12 | `detailed_type` (py, xml) | верно | `addons/product/models/product_template.py:58-65`; поля нет (grep — 0) | да (`product-type`) |
| 13 | `type-product`: `type == 'product'` | верно, узко | там же; сравнение молча всегда ложно. Не ловит домены `('type','=','product')` и vals | да (шире) |
| 14 | `sql_constraints` «(verify)» | верно; «(verify)» снимается; серьёзность занижена | `odoo/orm/model_classes.py:162-164` — игнорируется целиком; `models.Constraint` — `odoo/orm/table_objects.py:79` | да (ERROR) |
| 15 | `osv-expression` «(verify)» | верно (WARN) | `odoo/osv/__init__.py:4` и `odoo/osv/expression.py:173,242,248…` — DeprecationWarning «Since 19.0, use odoo.fields.Domain»; `Domain` в `odoo/fields/__init__.py:20` | **нет** |

**Итог:** 15 из 15 верны по сути, ложных нет. Неточности: 2 подсказки
(«(verify)» у верных фактов; «добавь `@odoo-module`»), 4 регэкспа уже, чем
нужно (4, 8, 9, 13), серьёзность не различается (ERROR и WARN печатаются
одинаково). Ошибочных правил 0.

**Чего у них нет, а у T2 есть (14):** `tree-view-ref`, `route-type-json`,
`partner-mobile-title`, `groups-fields`, `inherit-list-no-name`/`-implicit-name`,
`cron-numbercall`, `read-group`, `private-env`, `toggle-active`, `notify-progress`,
`api-returns`, `uom-fields`, `line-product-uom`, `manifest-hook-path`.

**Чего нет в T2 (кандидаты):**
1. `create-single` (из panus, №7) — ERROR. Самая ценная находка.
2. `oe-chatter` (№10) — WARN/ERROR «поведение пропадает».
3. `osv-expression` (№15) — WARN.
4. `assets-xml` (№1) — ERROR, но ловушка 15.0, модели сейчас её почти не делают.
5. `legacy-js` (№2) — только старая форма `odoo.define('x', function`; JS вне границы T2.
6. **Нашли сами по ходу сверки, у panus нет:** `_constraints = [...]` тоже
   игнорируется с warning (`odoo/orm/model_classes.py:159-161`) — ERROR в духе
   `sql-constraints` (проверка молча пропадает).

**Официальный источник правил.** В 19.0 есть `odoo/upgrade_code/` — скрипты
самого Odoo для `odoo-bin upgrade_code`: `17.5-01-tree-to-list.py`,
`18.1-00-sql-constraint.py`, `18.1-02-route-jsonrpc.py`,
`18.5-00-deprecated-properties.py` (`._cr/_uid/_context` → `.env.*`) и др. Это
готовый эталон для T2: каждое правило с автозаменой есть там. В отчёте T2 они
не упомянуты — передать.

### Другие тексты под 19.0 (выборочно)

- `patterns.md`: контроллер `type='json'` — в 19.0 устаревший алиас
  (`odoo/http.py:812-818`); советует `read_group` — в 19.0 deprecated
  (`odoo/orm/models.py:2754`). Под «version-aware» скилл это промах.
- `SKILL.md`: `self.env._()` «(verify)» — есть (`odoo/orm/environments.py:315`).
  `new_test_user` — есть (`odoo/tests/common.py:195`). `prefetch_fields` — есть.
- `SKILL.md`: «по умолчанию 18» и `check_compat.py`: версия из манифеста берётся
  только при ≥4 точках (`19.0.1.0.0`); `19.0.1.0` → `None` → цель 18 → правила 19
  молча не проверяются.
- `check_compat.py` не вырезает комментарии и docstring (ложные срабатывания),
  `migrations/` пропускает целиком.
- `scaffold.py` (читали, не запускали): под 19 — `<list>`, `<chatter/>`,
  `invisible=`, `models.Constraint` — верно. Но ставит `company_id` и
  `_check_company_auto` без мультикомпанийного record rule, хотя `SKILL.md`
  сам требует правило («multi-company ⇒ company_id + record rule»).
- `l10n-th.md` — Таиланд, нам не нужен.

### Сравнение с нашим

- **T2 `odoo19-lint`** (ветка `build/odoo19-lint`, `9705416`): 23 правила с
  цитатами 19.0, ERROR/WARN, вырезание комментариев, тесты, 0 ERROR на 8962
  файлах Odoo. Полностью покрывает 10 из 15 правил panus и шире по регэкспам.
- **`odoo19-mvp-build:code-dev` / `scaffolding`** (приватный
  `todoltd/claude-methodology-marketplace`): `add_repo` на чтение отклонён
  классификатором прав сессии. Сравнивали по описаниям в наших карточках
  (`catalog/dooservice-odoo-skills/README.md:119-134`): `code-dev` уже знает
  `models.Constraint`, `Domain`, `<list>`, `aggregator`, `jsonrpc`. Про
  `@api.model create` в доступных описаниях упоминания нет — проверить по
  оригиналу в T1. Из приватного репо ничего не копировали.
- **odoo-lens:** ~15 правил устаревшего API с теми же `name_get`,
  `user_has_groups`, `group_operator`, `tree_view_ref` — panus беднее.
- **odoo-agent-pro-kit:** L1–L6 для 19 — пересечение `<tree>`, `attrs`,
  `_sql_constraints`; у кита есть `type='json'`, у panus — нет.
- **dooservice-odoo-skills:** справочник 19.0 шире и точнее; правило «одна
  версия, без подстраховок» прямо противоположно идее panus «один скилл на
  16–20+».

### Вопросы и решения

- Приватный маркетплейс недоступен (отказ прав). Нужен ли доступ — решит
  пользователь; для вердикта не критично.
- Ничего чужого не запускали; A/B не делали: скилл не ставим, а правила
  переносятся в T2, где A/B уже идёт.

### Открытые вопросы

- Подтвердить на живом Odoo 19, что `@api.model def create(self, vals)` с
  `vals.get(...)` падает (по коду — да). Можно добавить в фикстуру T2.
- Есть ли `@api.model create` в `code-dev`/`scaffolding` шаблонах — сверить в T1.
