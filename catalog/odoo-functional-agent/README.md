# odoo-functional-agent

- **Тип:** плагин Claude Code (3 скилла, хуки, CLI `ofa` на Python stdlib)
- **Источник:** https://github.com/xmglord/odoo-functional-agent
- **Версия / коммит:** v0.1.3, `084b6900027348b161d55442feb778829ff29fa2` (2026-11-02)
- **Лицензия:** MIT (сверено по `LICENSE`, «Copyright (c) 2026 xmglord»; все 81 коммит одного автора, чужих файлов не нашли)
- **Дата разбора:** 2026-11-03
- **Вердикт:** **адаптировать** (только идеи и формат; ставить не будем)

## Что делает

Цепочка «бизнес-требование → план → ревью → применение → проверка» для Odoo 20
на локальной демо-базе. Модель пишет только файлы: `plan.json` (4 типа операций:
`install_modules`, `set_settings`, `upsert_record`, `call_method`, у каждой
`rationale` и `knowledge_refs`) и `plan.md` (обоснование по шаблону и таблица
«Test plan»). Дальше всё делает детерминированный CLI `ofa`: `validate` →
`lint-plan` (имена против базы и исходников 20.0) → **стоп на явное одобрение** →
`freeze` (SHA-256 плана) → `apply` (идемпотентно, с чтением назад) → `test`
(JSON-сценарии, роли, негативные тесты) → отчёт со «что не проверено».
Записать можно только в базу, которую `ofa` сам создал и пометил UUID.

## Какую слабость Claude закрывает

1. Пишет в «не ту» базу: тут позитивный список (имя `ofa_demo_*` + loopback +
   UUID-маркер в базе), а не запрет «если похоже на прод».
2. Принимает «сделай всё» или вопрос за одобрение: тут явные правила одобрения,
   хеш плана, повторное одобрение после любой правки.
3. «Применилось» ≠ «держится»: чтение назад после записи (`VALUE_NOT_HELD`) и
   флаг `pre_state` («уже было в шаблоне — ничего не доказывает»).
4. Тестирует под админом, который обходит согласования: роли на отдельных
   тестовых пользователях без админ-групп, негативные тесты с точным текстом ошибки.
5. Имена полей из старых версий: линтер против живой базы и индекса исходников.

## Компоненты

| Компонент | Что это | Карточка | Ценность для нас |
|---|---|---|---|
| `odoo-functional` + `ofa apply` | Цепочка план → одобрение → freeze → apply | [items/plan-approve-apply.md](items/plan-approve-apply.md) | **высокая** (формат и правила) |
| Guard: слой a + хук + конфиг сервера | Защита от записи не туда | [items/demo-guard.md](items/demo-guard.md) | **высокая** (маркер стенда) |
| «Test plan» + сценарии `ofa test` | Покрытие требований тестами, роли, `expect_error` | [items/test-plan-scenarios.md](items/test-plan-scenarios.md) | средняя–высокая |
| `ofa lint-plan` | Проверка имён плана против базы и исходников | [items/lint-plan.md](items/lint-plan.md) | средняя (дублирует T2) |
| `knowledge/20.0` + `odoo-explain` | Справочник 42 статьи, список дрейфов 20.0 | [items/knowledge-drifts.md](items/knowledge-drifts.md) | средняя (для 20.0) |
| `help` | Справка и проверка готовности через `ofa-check` | — | низкая |

## Как устроен

- **Скиллы:** `odoo-functional` (215 строк, 8 фаз), `odoo-explain` (только чтение),
  `help`. Описание `odoo-functional` очень широкое («use whenever the user brings a
  business case … in any language», включая RFP) — срабатывает на всё про Odoo.
- **CLI `ofa`:** ~4 тыс. строк stdlib-Python в `src/ofa/`, тесты в `tests/`
  (не запускали). Ходит в Odoo только по JSON-2 (`/json/2/<model>/<method>`,
  bearer-ключ) на loopback; запускает `odoo-bin`, `psql`/`createdb`, `git`.
- **Хуки:** `PreToolUse` (`Bash`, `Skill`, firefox-devtools), `UserPromptSubmit`,
  `SessionStart`/`SessionEnd` (clear/compact/fork). Срабатывают во всех сессиях
  машины; блокируют только после «активации» сессии.
- **Ставит на машину:** `bin/ofa`, `bin/ofa-check` в PATH; `~/.config/ofa/`
  (конфиг, ключи API), `~/.cache/ofa/` (индекс исходников), маркеры в
  `${CLAUDE_PLUGIN_DATA}`; локальный Odoo-процесс и базы в Postgres.
- **Сеть/телеметрия:** только loopback-Odoo; телеметрии нет. Скриншоты — через
  внешний Firefox DevTools MCP (опционально).
- **Требует:** свой checkout Odoo 20.0 (+ Enterprise для всех 5 примеров),
  Postgres, Python 3.11+. В облачной сессии без локального Odoo не работает.

## Проверка

Практический прогон не делали (чужой код и хуки запускать без разрешения нельзя;
локального Odoo 20 нет). Заявленные результаты примеров проверить по репо
нельзя: ссылки на `runs/<run_id>/report.md` ведут в каталог из `.gitignore`.

| Задача | Без него | С ним |
|---|---|---|
| — | не мерили | не мерили |

## Сравнение с нашим

| Наше | Что у них сверх | Что у нас лучше / дублирует |
|---|---|---|
| `odoo19-sales-demo:demo-base-builder` (читали, `sale_todo_claude@2a7f7c1`) | Позитивный маркер базы вместо «стоп, если `web.base.url` = прод»; хеш одобренного плана; `pre_state`; чтение назад как правило исполнителя, а не текста | У нас: уровни базы 1–3, поиск перед созданием по естественному ключу, пакеты с контрольным счётом, «знимок» как доказательство для продаж, Studio как разработка. Их «search before create» = наш `match`/`adopted` |
| `odoo19-sales-demo:demo-build-plan` (по описанию) | Формат решения: Business reason / What Odoo does / Pre-state / Alternatives / Pitfalls / Sources; «Not covered by this plan» | Наш план — про показ клиенту (что демонстрируем), а не про операции; цели разные |
| `odoo19-mvp-build:config-spec` / `config-runbook` (по описанию, код не читали) | Машиночитаемый план операций с `rationale` + `knowledge_refs`, `skip_if` для методов, запрет `$create`, `depends_on` | — проверить по маркетплейсу |
| `odoo19-mvp-build:config-review` (по описанию) | Линтер имён против базы и исходников; «Names to review» в стопе ревью | Пересекается с T2 (линтер-барьер) |
| `odoo19-mvp-build:testing` / T11 `uat-test-book` | «Test plan» на каждую потребность, **Not tested** с причиной; роли без админ-групп; `expect_error` с текстом из исходника | — |
| `odoo-connector` / Odoo MCP (F1, T3) | Проверка на стороне клиента до первого вызова: имя, хост, UUID-маркер; ключи только у демо-баз | У нашего MCP есть мультибаза и `connection_id` на каждый вызов, подтверждение удаления; erpipe даёт allowlist `model.method` и аудит (T3). Их guard — только для своих баз |

## Оценка

| Критерий | Балл (0–3) | Комментарий |
|---|---|---|
| Прирост | 2 | Правила одобрения, маркер, `pre_state`, Not tested меняют действие; не измерено |
| Частота | 2 | Демо-стенды и конфиги MVP — регулярно, но у нас Odoo 19 и удалённые стенды |
| Надёжность | 1 | Не запускали; тесты только авторские; отчёты прогонов не в репо |
| Стоимость контекста | 1 | Хуки на каждый Bash/Skill/промпт во всех сессиях (запуск Python); широкий триггер; скилл 215 строк |
| Безопасность | 2 | Код прочитан, сеть только loopback, телеметрии нет; но ставит CLI в PATH, поднимает Odoo, хуки во всех сессиях |
| Поддержка | 1 | Один автор, 0★, неделя жизни (2026-10-26 → 11-02), активен |
| **Итого** | **9/18** | Адаптировать |

## Что взять

Лицензия MIT: можно и перевод с атрибуцией. Атрибуция в `references/attribution.md`
целевого скилла. Сверка фактов Odoo 19 — в `notes.md` (файл:строка).

| # | Идея | Источник (`путь@SHA`) | Что берём | Куда у нас | Как | Лицензия |
|---|---|---|---|---|---|---|
| 1 | **Маркер демо-стенда** (позитивный список) | `docs/guard.md@084b690` «Layer a»; `src/ofa/client.py@084b690` (`open_client`), `src/ofa/guard.py@084b690` | При создании стенда пишем UUID в `ir.config_parameter` (19.0: `set_param`), храним в реестре стендов; перед **каждым** сеансом записи сверяем `get_param` с реестром; нет/не совпал/не читается → стоп (не «похоже ли на прод») | T3 `odoo-connector` (серверная проверка) + Шаг 0 `demo-base-builder` | пересказ своими словами | MIT ✓ |
| 2 | **Правила одобрения** + хеш плана | `skills/odoo-functional/SKILL.md@084b690` Phase 4–5; `docs/plan_format.md@084b690` (`freeze`, `NOT_APPROVED`, `HASH_MISMATCH`) | «Вопрос, комментарий, молчание, давнее "делай всё" — не одобрение»; правка плана → повторное одобрение; цитата одобрения в отчёте; хеш плана в шапке и в отчёте | `config-runbook`, `demo-build-plan` → `demo-base-builder` | перевод/адаптация с атрибуцией | MIT ✓ |
| 3 | **`pre_state` и чтение назад** | `docs/plan_format.md@084b690` «Result statuses»; `src/ofa/executor.py@084b690` (`_check_held`) | После записи читать поля назад, «не удержалось» = ошибка; операция, которая была выполнена ещё до плана, помечается «ничего не доказывает» | `demo-base-builder` (знимок), `config-review` | пересказ | MIT ✓ |
| 4 | **Test plan с Not tested** | `skills/odoo-functional/plan_md_template.md@084b690` («Test plan»); `SKILL.md` Phase 6, 8 | Каждая потребность — строка: сценарий + что проверяет, или **Not tested** с причиной; в отчёте — список расхождений с одобренным Test plan | `odoo19-mvp-build:testing`, T11 `uat-test-book` | перевод/адаптация | MIT ✓ |
| 5 | **Роли не-админы и негативные тесты** | `docs/plan_format.md@084b690` «Test identities»; `SKILL.md` Phase 6 | Админ обходит согласования → роль на отдельном тест-пользователе с `$set` групп, без `base.group_system`/`group_erp_manager`; негатив = класс исключения + текст из исходника или прогона, не угаданный | `testing`, `uat-test-book`, `config-review` | пересказ | MIT ✓ |
| 6 | **Шаблон решения в плане** | `skills/odoo-functional/plan_md_template.md@084b690` | Decision: Business reason / What Odoo does (модели, поля, settings) / Pre-state / Alternatives / Pitfalls / Sources (или «Uncited») + «Not covered by this plan» | `config-spec` | перевод/адаптация | MIT ✓ |
| 7 | **Список дрейфов 19→20** | `knowledge/README.md@084b690` «Known 20.0 drifts» | Только как вход для T1/T2 на 20.0; 9 пунктов перепроверены по `odoo/odoo` (notes.md), берём факты с нашей ссылкой `файл:строка` | `source-check` / справка T1 (раздел 20.0) | только факты, сверенные заново | MIT ✓ (факты не охраняются) |
| 8 | **Линтер: `ir.model.fields`, а не `fields_get`** | `docs/plan_format.md@084b690` «lint-plan»; `src/ofa/lint.py@084b690` | `fields_get` прячет поля по группам (19.0 `odoo/orm/models.py:3364`) → проверка имён по `ir.model.fields`; коды `NOT_IN_x` / `NEEDS_MODULE`; ошибки плана блокируют, проза — предупреждения в «Names to review» | T2 (линтер-барьер) | идея | MIT ✓ |
| 9 | **Cron не смотрит на `dbfilter`** | `docs/guard.md@084b690` «Server hardening» | Для стендов на общем Postgres: `max_cron_threads = 0` или `db_name`, иначе cron стенда гоняет чужие базы (19.0 `odoo/service/server.py:99-100`) | заметка для админов стендов / `demo-base-builder` §стенд | факт, сверен | — |

**Не берём:** хук-guard (always-on, pattern matching, рассчитан на локальный
Odoo и Bash; у нас запись идёт через MCP, и барьер нужен в сервере, T3);
CLI `ofa` (Odoo 20, loopback); справочник `knowledge/20.0` целиком (20.0 и
фокус на Мексике); описание `odoo-functional` (слишком широкий триггер).

## Риски и заметки

- Хуки плагина работают во всех сессиях машины, где он установлен, и при
  сбое `python3` в «активной» сессии блокируют любой Bash.
- Защита хука — сопоставление шаблонов; автор честно перечисляет дыры
  (скрипт на диске, git-алиасы, клики в браузере).
- Все 5 примеров на Enterprise; Community целиком не прогонялся.
- Перенос на 19.0: JSON-2 есть и в 19.0 (`addons/rpc/controllers/json2.py:49-53`),
  но `get_str` → `get_param`, `ir.access` → `ir.model.access` + `ir.rule`,
  `uom_id` → `product_uom(_id)`, `store_by` → `tracking`; `ODOO_SERIES = "20.0"`
  зашит в `src/ofa/__init__.py`.
