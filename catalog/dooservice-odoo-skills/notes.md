# Рабочий журнал: dooservice/odoo-skills

Дата: 2026-11-03. Коммит разбора: `f154564` (2026-10-31), 162 коммита
с 2026-10-09, один автор (Josuesp1620, dooservice). ★2.

## Что смотрели

- Клон во временный каталог (scratchpad), только чтение. `install.sh`,
  `tools/*.py`, CI и evals не запускали.
- Структура: `odoo/<16.0..20.0>/` (сгенерировано), `odoo/common/` (руками),
  `.claude-plugin/marketplace.json` (5 плагинов `odoo-16` … `odoo-20`),
  `tools/` (генераторы), `evals/` (кейсы `claude plugin eval`), `docs/case-study/`.
- В плагине только Markdown: нет `hooks`, `.mcp.json`, `settings.json`,
  скриптов внутри скиллов. Внешних URL в текстах скиллов нет (кроме ссылок
  Odoo в самих xmlid/моделях website).

## Проверка гипотезы «скиллы самой Odoo»

Подтверждается частично и честно описано в README («Derived from Odoo's skill
library (odoo/odoo, branch 20.0, `skills/`), by Odoo S.A., LGPL-3 … Not
affiliated with Odoo S.A.»).

- Клонировал `odoo/odoo` ветки 20.0 (sparse, коммит `b9823b8`, 2026-10-30):
  каталог `skills/` есть, 24 файла, ~58 КБ: `odoo-guidelines`,
  `odoo-web-guidelines`, `odoo-security`, `odoo-review`, `odoo-git` + README.
  В ветке 19.0 (`e0b25b7`) каталога `skills/` нет.
- `tools/guidelines/UPSTREAM` фиксирует, от какого коммита Odoo сгенерировано
  (`skills 479b1c8…`); `tools/upstream.py` показывает, что изменилось у Odoo.
- От Odoo: 5 скиллов (тексты переработаны шаблонами под каждую версию).
  Своё у dooservice: `odoo-reference` (генерируется из исходников версии),
  `odoo-functional` (70 рецептов настройки, руками), `odoo-upgrade`,
  таблица `version.md`, evals, бюджеты размеров слоёв.
- Адаптация осмысленная: `odoo-review` у Odoo ориентирован на репозиторий
  самой Odoo (community + enterprise «две половины», master/stable), у
  dooservice — на проект клиента (`git merge-base`, сабмодули, «модуль уже
  установлен в важной БД»). `odoo-git` у dooservice тоже для проектного репо.

## Сверка фактов Odoo 19 с исходниками 19.0

Sparse-checkout `odoo/odoo@19.0` (`e0b25b7`). Всё из `version.md` 19.0 и
описания `odoo-reference`, что проверял, совпало:

| Утверждение | Где в 19.0 | Итог |
|---|---|---|
| `_sql_constraints` игнорируется с warning | `odoo/orm/model_classes.py:162` | да |
| `models.Constraint/Index/UniqueIndex` | `odoo/orm/table_objects.py:79,125,185`, экспорт в `odoo/models/__init__.py` | да |
| `from odoo.fields import Domain` | `odoo/fields/__init__.py:20` | да |
| `res.users.group_ids`, `all_group_ids` | `res_users.py:257-258` | да |
| `res.groups.privilege_id` → `res.groups.privilege` | `res_groups.py:36`, `res_groups_privilege.py` | да |
| route `json` — устаревший алиас `jsonrpc`, есть `json2` | `odoo/http.py:814,2633` | да |
| `attrs`/`states` → ValidationError | `ir_ui_view.py:495` | да |
| `t-raw` пишет deprecation warning | `ir_qweb.py:2499` | да |
| `group_operator` → `aggregator` (DeprecationWarning) | `odoo/orm/fields.py:485` | да |
| нет `account.fiscal.position.tax`; `fiscal_position_ids`/`original_tax_ids` на налоге | `account_tax.py:95,101`; grep по `addons/account/models` пуст | да |
| нет `hr.expense.sheet` | `addons/hr_expense/models/` без упоминаний | да |
| `account.reconcile.model.trigger` manual/auto_reconcile, нет `rule_type` | `account_reconcile_model.py:110` | да |
| UoM `relative_factor`, `relative_uom_id` | `uom_uom.py:36,41` | да |
| payment term `nb_days`, `delay_type` | `account_payment_term.py:294,307` | да |
| `sale.order.line.tax_ids` | `sale_order_line.py:162` | да |
| `price_include_override='tax_included'` | `account_tax.py:142,334` | да |
| `is_storable` (в `stock`) | `addons/stock/models/product.py:834` | да |
| `hr.leave.type.requires_allocation` Boolean, `allocation_validation_type` hr/manager/both/no_validation | `hr_leave_type.py:92,96` | да |
| `base.automation`: `on_write` устарел, `on_create_or_write` | `base_automation.py:183-184` | да |
| тест-теги по умолчанию `standard`, `at_install` | `odoo/tests/common.py:317` | да |
| Owl 2 в 19.0 | `addons/web/static/lib/owl/owl.js:5869` → `2.8.4` | да |

Расхождений не нашёл. Выборка ~20 утверждений; рецепты `odoo-functional`
проверены точечно (fiscal position: шаги и поля совпадают с `account_tax.py`).

## Безопасность

- Скиллы — только текст. Ни сети, ни телеметрии, ни хуков.
- `install.sh` (не запускали): `curl | bash` → `npx -y skills@1 add …` —
  мажорный пин, не точный; нам не нужен, ставить через marketplace или копией.
- `odoo-functional/connect.md` учит безопасной работе с БД: читать до записи,
  dry-run с `env.cr.rollback()`, «да» пользователя перед массовыми
  изменениями, SQL только на чтение, архивировать вместо удаления. Это плюс.
- CI: `uvx skills-ref==0.1.1`, `npx @anthropic-ai/claude-code@2.1.304` — пины точные.

## Стоимость контекста

- Описания 8 скиллов версии 19.0 + common: ~4.6 тыс. символов (~1.2 тыс.
  токенов) всегда в контексте.
- Тела: `SKILL.md` 2.5–12 КБ; `odoo-guidelines` 256 КБ (29 файлов),
  `odoo-reference` 4 МБ на версию (688 файлов) — читается grep-ом по строкам,
  целиком не грузится. По их замерам скиллы добавляют ~40 тыс. токенов на
  задачу (Haiku, 19.0, v2.0.0).

## Их собственные замеры (не наши)

`evals/RESULTS.md`, regex-грейдеры (файл есть, нужное имя есть, имени другой
версии нет). 19.0: Haiku 77.6% → 96.1% (+18.5), Sonnet 94.4% → 100% (+5.6, на
версии 1.1.0). Прирост тем больше, чем новее версия и слабее модель.

## Сравнение с нашими

Сначала `~/.claude/plugins/synced/*/` оказался пуст. По подсказке главной сессии
подключил приватный `todoltd/claude-methodology-marketplace` на чтение (`add_repo`,
клон `/home/user/claude-methodology-marketplace`, `7acde054afadf0ebaecc508ea3c41c6d93d65605`,
2026-11-03) и прочитал оригиналы `odoo19-mvp-build/skills/{code-dev,pr-review,testing,security-review}`.
Текст оттуда в наш публичный репо не копирую, только выводы.

- `security-review` в маркетплейсе совпадает с нашим `proposals/.../proposed/SKILL.md`
  (`diff -q` пустой): Strix-версия уже применена.
- `pr-review`: вставка дисциплины ревью уже применена (раздел «Review discipline»,
  «Quality floor», «Prove-It»).
- `testing`: `@tagged('post_install', '-at_install')` есть и совпадает с dooservice;
  hoot и «в 19.0 по умолчанию `at_install`» явно не сказаны.
- **`code-dev/references/odoo-version-notes.md`, раздел Odoo 19: ошибки**, проверено
  по `odoo/odoo@e0b25b7`:
  - Python/PostgreSQL: у нас 3.12+/16+, в `odoo/release.py:39,41` 3.10 и 13;
  - упомянут тип поля для AI-подсказок: в `odoo/fields`, `odoo/orm` такого нет;
  - «`discuss` отделён от `mail`»: аддона `discuss` в 19.0 нет (`git ls-tree addons/`);
  - реальные ловушки 19.0 (`models.Constraint`, `group_ids`, `jsonrpc`, `Domain`) не названы.
- `pr-review`, «Version-specific checks → Odoo 19+»: проверка «`mail` вместо
  `discuss`» ложная (следствие той же ошибки).
- Похоже, этот раздел написан по памяти модели: это ровно та слабость, которую
  закрывает dooservice.

## Открытые вопросы

- Будут ли `odoo-19` и наш `odoo19-mvp-build` конфликтовать по триггерам
  (оба на «пишу код Odoo 19»)? Нужен прогон с обоими.
- LGPL-3 на текст: копирование файлов в `boost` (MIT) делает эти файлы LGPL;
  проще ставить их плагин отдельно, а у себя писать своими словами.

## A/B (2026-11-03)

4 задачи из `evals/odoo-19` (fiscal position, expense, reconcile model, group
privilege), 8 субагентов текущей модели, по 1 прогону, без сети и без исходников.
«С ним»: список описаний 8 скиллов, папка скиллов, грузить на своё усмотрение.
Ответы в scratchpad (`ab/`), не в репо.

- Со скиллами: все 4 загрузили нужное (`odoo-functional` + рецепт + grep
  `odoo-reference`; для групп `odoo-guidelines/security.md`). Код только 19.0.
  Regex-грейдеры авторов дали бы 3 ложных провала: старые имена только в
  комментариях «X нет в 19.0».
- Без скиллов: имена 19.0 верны во всех 4, но в fpos/expense/reconcile есть
  ветки для ≤18 (`tax_src_id`, `hr.expense.sheet`, `rule_type='writeoff_button'`).
- Токены субагентов: без ~61 тыс., с ~77 тыс. (среднее по 4).
- Решение: прирост для сильной модели есть, но в чистоте и уверенности, а не в
  знании имён. Для «взять» как есть мало: нужен прогон с `odoo19-mvp-build` вместе.

## Сообщения главной сессии (2026-11-03)

1. Новый п. 5 правил: в README карточки URL, SHA, лицензия, дата; в «Что взять»
   у каждой идеи: исходный `путь@SHA`, что, куда, как, позволяет ли лицензия.
   Сделано: таблица «Что взять» в README.
2. Где брать тексты наших плагинов: `proposals/`, `sale_todo_claude` (продажи,
   не нужны для этого разбора), приватный маркетплейс через `add_repo`.
   Подключился на чтение, см. выше. Из приватного репо ничего не скопировано.
