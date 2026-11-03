# dooservice/odoo-skills: скиллы Odoo 16–20

- **Тип:** набор скиллов (Agent Skills) + marketplace Claude Code (плагины `odoo-16` … `odoo-20`)
- **Источник:** https://github.com/dooservice/odoo-skills (★2)
- **Версия / коммит:** `f154564bea7f61f77210792e49cdb720d7aeb8fa` (2026-10-31), скиллы v2.0.0
- **Лицензия:** LGPL-3.0-only (производное от `odoo/odoo@b9823b8a6ed7f33c4450ac6dbe2dabed3ca6a6e7:skills/`, Odoo S.A., LGPL-3)
- **Дата разбора:** 2026-11-03
- **Вердикт:** **адаптировать** (идеи и проверенные факты 19.0 перенести к себе). Плагин
  `odoo-19` можно дать разработчикам как необязательный справочник после
  прогона вместе с `odoo19-mvp-build`, но не ставить всем как есть.

## Что делает

Даёт агенту знания конкретной версии Odoo: правила кода (Python/ORM, XML, права,
тесты), правила веба (Owl, реестры, hoot), чек-лист безопасности, процесс ревью,
коммиты, миграции, 70 рецептов функциональной настройки без кода и сгенерированный
из исходников справочник всех моделей, полей, Settings и XML id Community-версии.
Главная мысль: модель пишет код «не той версии» (`<tree>` в 19, `_sql_constraints`,
`hr.expense.sheet`), а здесь у каждой версии своя таблица отличий, сверенная с
исходниками.

## Происхождение (гипотеза проверена)

**Подтверждено частично, и автор пишет об этом прямо.** В `odoo/odoo` ветки 20.0
(коммит `b9823b8`) есть каталог `skills/` от Odoo S.A.: 5 скиллов, 24 файла, ~58 КБ
(`odoo-guidelines`, `odoo-web-guidelines`, `odoo-security`, `odoo-review`,
`odoo-git`). В ветке 19.0 этого каталога нет. dooservice взял эти 5 скиллов
(коммит-источник записан в `tools/guidelines/UPSTREAM`), переложил их на шаблоны и
перегенерировал под 16.0–20.0. Свои у dooservice: `odoo-reference`,
`odoo-functional`, `odoo-upgrade`, таблицы `version.md`, evals. Сам набор не от
Odoo S.A.: автор один (dooservice, хостинг Odoo), README оговаривает «Not
affiliated with Odoo S.A.».

## Состав (версия 19.0 + common)

| Скилл | Откуда | Объём | Суть | Нам | Карточка |
|---|---|---|---|---|---|
| `odoo-guidelines` | Odoo 20.0 → 19.0 | 29 файлов, 256 КБ | Правила кода по доменам + `version.md` (что есть в 19.0) | **адаптировать**: таблицу 19.0 и правило «одна версия, без подстраховок» | [items/odoo-guidelines.md](items/odoo-guidelines.md) |
| `odoo-reference` | своё, генератор | 688 файлов, 4 МБ | Модели/поля/методы/XML id/Settings Community 19.0, поиск grep-ом | взять как справочник (через плагин); идея для `odoo-model-map` | [items/odoo-reference.md](items/odoo-reference.md) |
| `odoo-functional` | своё | 74 файла, ~1 МБ | 70 рецептов настройки через ORM / `odoo-bin shell` | **адаптировать** `connect.md` (dry-run, «да» до записи); рецепты в справочник | [items/odoo-functional.md](items/odoo-functional.md) |
| `odoo-security` | Odoo | 225 строк | Чек-лист безопасности аддона | **адаптировать**: добавить отсутствующие у нас пункты в `security-review` | [items/odoo-review-security.md](items/odoo-review-security.md) |
| `odoo-review` | Odoo, переработан | 1 файл | Ревью: пин коммита → файл → разделы правил → два прохода | **адаптировать** в `pr-review` | [items/odoo-review-security.md](items/odoo-review-security.md) |
| `odoo-web-guidelines` | Odoo | 13 файлов | Owl, patch, реестры, сервисы, hoot | справочно; JS у нас редко | — |
| `odoo-git` | Odoo, для проектного репо | 1 файл | `[TAG] module:`, тело «почему» | отклонить: у нас свои правила коммитов | — |
| `odoo-upgrade` | своё | 1 файл | Порт модулей, миграционные скрипты | отложить до задач миграции | — |

## Какую слабость Claude закрывает

Путаница версий Odoo. Сильная модель по нашему A/B имена 19.0 знает, но не уверена
в версии и пишет подстраховочный код на несколько версий (`if 'rule_type' in
fields`). Слабая (Haiku) просто пишет имена 20.0 или 16.0: по их замерам на 19.0
без скиллов выходит 77.6%, со скиллами 96.1%.

## Как устроен

- Только Markdown: нет хуков, MCP, скриптов внутри скиллов, сети, телеметрии.
- Слоями: описание всегда в контексте и уже содержит самые изменчивые имена
  версии (~1.2 тыс. токенов на 8 скиллов) → `SKILL.md` как карта «задача →
  файл» → файл открывается списком ключевых имён и разделов → справочник ищется
  grep-ом, целиком не читается. Бюджеты слоёв проверяет `tools/check_budgets.py` в CI.
- Генераторы в `tools/` (не часть скиллов): тексты гайдлайнов — шаблоны с
  `$name` и классом на файл, справочник собирается из checkout каждой ветки,
  `build_coverage.py` проверяет, что каждый модуль Community и каждый элемент
  фреймворка чем-то покрыт (`COVERAGE.md`: пропусков 0).
- `install.sh` = `curl | bash` → `npx -y skills@1 add` (пин только мажорный). Не нужен:
  есть marketplace или копирование папок.

## Проверка

### Точность фактов 19.0

~20 утверждений из `version.md` и описания `odoo-reference` сверены с
`odoo/odoo@19.0` (`e0b25b7`), файл и строка в [notes.md](notes.md). Расхождений
**0**: `models.Constraint`, `Domain`, `group_ids`/`privilege_id`, `jsonrpc`/`json2`,
нет `account.fiscal.position.tax` и `hr.expense.sheet`, `trigger` у reconcile model,
UoM `relative_factor`, Owl 2.8.4, теги тестов `at_install` и т.д.

### A/B (наш, мини)

4 задачи из их `evals/odoo-19`, по одному прогону, субагенты нашей текущей модели,
без сети и исходников. «С ним» — список описаний скиллов, остальное агент грузит сам.

| Задача | Без него | С ним |
|---|---|---|
| fiscal position 15% → 0% | имена 19.0 верные, но ветка `if 'account.fiscal.position.tax' in env` с `tax_src_id` для ≤18 | только путь 19.0, проверка `map_tax` |
| расход 45.00 + submit/approve | верно для 19.0 + ветка с `hr.expense.sheet` | только 19.0; разобраны крайние случаи (нет одобряющего → одобряется при submit) |
| reconcile model «Bank charges» | `trigger='manual'` + условный `rule_type='writeoff_button'` | только `trigger='manual'`, блок «как откатить» |
| группы под privilege | `privilege_id`, верно | `privilege_id`, верно, короче |
| **Итог** | имена верны 4/4, чистый код под одну версию 1/4 | 4/4 и 4/4 |
| Цена (токены субагента) | ~61 тыс. | ~77 тыс. (**+26%**) |

Скиллы загружали во всех 4 прогонах (`odoo-functional` + рецепт + grep по
`odoo-reference`). Regex-грейдеры авторов засчитали бы «С ним» как провал: старые имена
встречаются там в комментариях «X в 19.0 нет». Вывод: для сильной модели прирост в
**чистоте и уверенности**, а не в знании имён; для Sonnet/Haiku прирост большой
(их замеры). Выборка мала: 1 прогон на ячейку.

## Оценка

| Критерий | Балл (0–3) | Комментарий |
|---|---|---|
| Прирост | 2 | Сильная модель: убирает подстраховки под чужие версии, добавляет откат/проверку; слабая: +18 п. (их замеры) |
| Частота | 3 | Odoo 19 у нас каждую неделю: код, ТР, настройка |
| Надёжность | 2 | Подгрузка 4/4 у нас; у них отказы — прогоны, где агент не загрузил скилл |
| Стоимость контекста | 2 | ~1.2 тыс. токенов описаний всегда; +~15 тыс. на задачу |
| Безопасность | 3 | Только текст; прочитан; рецепты требуют dry-run и «да» до записи |
| Поддержка | 2 | Очень активен (162 коммита за 3 недели), CI, evals; но 1 автор, ★2, проекту 3 недели |
| **Итого** | **14/18** | |

## Сравнение с нашими

Оригиналы `odoo19-mvp-build` прочитаны в `todoltd/claude-methodology-marketplace@7acde054afadf0ebaecc508ea3c41c6d93d65605`
(приватный, подключён на чтение; текст сюда не копируется, только выводы).

| Наш | Что у них сверх | Что у них хуже / нет | Пересечение |
|---|---|---|---|
| `boost:source-check` | Готовая офлайн-таблица отличий 19.0, сверенная по исходникам | Нет URL-цитат и `UNVERIFIED`: факты даны как есть | Обе против «по памяти» |
| `boost:odoo-model-map` | Справочник *стандартных* моделей/полей/xmlid 19.0 без checkout | Не видит наш `td.*` и связи проекта | Дополняют друг друга |
| `odoo19-mvp-build:code-dev` (+ `references/odoo-version-notes.md`) | Точная таблица 19.0: `models.Constraint` (`_sql_constraints` игнорируется), `Domain`, `group_ids`, `privilege_id`, `jsonrpc`/`json2`, `self.env._()`, `<list>`, `aggregator` | Нет AC/SPEC, TODO-маркеров, правил ToDo | Шаблоны computes/constraints/create. **Наш раздел «Odoo 19» в version-notes содержит ошибки** (см. ниже) |
| `odoo19-mvp-build:pr-review` | Шаг «файл → раздел правил», «код, которого diff не показывает» (grep переопределений и переименований), merits pass, строка «прочитанные правила» | Нет SPEC/AC, нет вердикта BLOCK | Дисциплина ревью (наш INSERT уже применён) близка к их шагам 5–7. **Наши «Odoo 19+» проверки частично неверны** |
| `odoo19-mvp-build:testing` | Явно: в 19.0 тег по умолчанию `at_install`; JS-тесты hoot (`*.test.js`) | Нет «тест на каждый AC» | `@tagged('post_install', '-at_install')` у нас уже есть: совпадает |
| `odoo19-mvp-build:security-review` (Strix-версия уже в маркетплейсе) | Markup-XSS, field `groups`, публичные методы = RPC, domain injection, `file_open`, возврат сложных объектов, `getattr/setattr`, pickle, тайминг | Нет методологии закрытия и severity | ACL/`sudo`/SQL/routes |

### Ошибки в наших текстах (проверено по `odoo/odoo@e0b25b7032aacb5bf711a119c40a466888e2fc16`, ветка 19.0)

Найдены при сверке с dooservice; это **самая полезная находка разбора**.

| Наш файл | Утверждение (кратко) | Факт в 19.0 |
|---|---|---|
| `code-dev/references/odoo-version-notes.md`, раздел Odoo 19 | Python 3.12+, PostgreSQL 16+ | `odoo/release.py:39,41`: `MIN_PY_VERSION = (3, 10)`, `MIN_PG_VERSION = 13` |
| там же | новый тип поля для AI-подсказок | такого поля в `odoo/fields`, `odoo/orm` нет |
| там же | модуль `discuss` отделён от `mail`, проверять depends | аддона `discuss` в 19.0 Community нет, есть `addons/mail` |
| `pr-review/SKILL.md`, «Version-specific checks → Odoo 19+» | флаг «`mail` вместо `discuss`» | то же: ложная проверка даст ложные REQUEST CHANGES |
| `code-dev/references/odoo-version-notes.md` | раздел 19 не называет реальные ловушки | нет `models.Constraint`, `_sql_constraints` игнорируется (`odoo/orm/model_classes.py:162`), `group_ids` (`res_users.py:257`), `type='jsonrpc'` (`odoo/http.py:814`), `Domain`, `<list>` |

Правку делает владелец маркетплейса; предлагаемая замена — своя таблица фактов (п. 1 ниже).

## Что взять

Все исходные пути ниже в `dooservice/odoo-skills@f154564bea7f61f77210792e49cdb720d7aeb8fa`,
если не указано иное. LGPL-3 позволяет использовать идеи и факты свободно; дословная
копия файла в `boost` (MIT) сделала бы этот файл LGPL с обязательствами по
распространению, поэтому везде «пересказ» или «только идея».

| # | Исходный файл | Что берём | Куда у нас | Как | Лицензия |
|---|---|---|---|---|---|
| 1 | `odoo/19.0/odoo-guidelines/guidelines/version.md` | Перечень версионных ловушек 19.0 | `plugins/boost/skills/source-check/references/odoo19-facts.md` и замена раздела 19 в `odoo19-mvp-build:code-dev/references/odoo-version-notes.md` | Своя таблица: факт + `файл:строка` в `odoo/odoo@e0b25b7` (набросок в `notes.md`); факты проверены нами | да: факты и идея, текст свой |
| 2 | `odoo/common/odoo-functional/SKILL.md` («Rules that save databases»: one version, no fallbacks) | Правило «одна версия, без подстраховок под другие» | `odoo19-mvp-build:code-dev` (раздел Spec discipline), `boost:lean-change` | Пересказ своими словами, 1–2 строки | да: только идея |
| 3 | `odoo/19.0/odoo-security/SKILL.md` (разделы Field-level access, Default to private methods, Domain injection, Prevent XSS, `file_open`, `eval`, complex objects, `getattr`, pickle, timing) | 8–10 пунктов чек-листа, которых у нас нет | `odoo19-mvp-build:security-review`, Step B | Пересказ; атрибуция идеи «Odoo S.A., `odoo/odoo@b9823b8:skills/odoo-security`» в `references/ATTRIBUTION.md` | да: пересказ + атрибуция |
| 4 | `odoo/19.0/odoo-review/SKILL.md` (Process 2–5, «Code the diff never shows») | Шаг «файл → раздел правил», три grep-а потребителей, merits pass, строка «прочитанные правила» | `odoo19-mvp-build:pr-review` (Review discipline / Dimension 3) | Пересказ своими словами | да: пересказ |
| 5 | `odoo/common/odoo-functional/connect.md`, `SKILL.md` (The method) | Dry-run с `env.cr.rollback()`, не делать dry-run необратимых внешних действий, «да» до записи, архив вместо удаления, заметка с откатом | `odoo19-implementation`, инструкции к `odoo-connector` | Пересказ | да: только идея |
| 6 | `odoo/19.0/*/SKILL.md` (frontmatter `description`) | Приём: в описании 6–10 самых изменчивых имён версии | описания наших `odoo19-*` скиллов | Только идея | да |
| 7 | `evals/odoo-19/*/graders/*.md` | Regex-грейдеры `not_contains` (имя чужой версии) + `contains` (имя этой) | `plugins/boost/evals/` для Odoo-скиллов | Только идея (учесть ложные срабатывания на комментариях) | да |
| 8 | весь плагин `odoo-19` (`.claude-plugin/marketplace.json`) | Справочник `odoo-reference` + рецепты как есть | опционально разработчикам, отдельным плагином с пином коммита | Установка, без копирования | да: используем, не распространяем |

## Риски и заметки

- **LGPL-3**: см. «Что взять»: только пересказ и идеи; их текст лишь через их плагин.
- Широкие описания («Read before writing any Python, XML or CSV for Odoo 19.0»)
  будут конкурировать с нашими скиллами `odoo19-*`.
- Проект молодой, автор один: при установке пин на коммит.
- Enterprise не покрыт (справочник только Community), локализации `l10n_*` тоже.
