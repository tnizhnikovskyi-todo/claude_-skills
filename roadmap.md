# План внедрения

Что из найденного мы применяем на практике. Составлен 2026-11-02 по итогам
первого прохода (13 репозиториев, см. [`synthesis.md`](synthesis.md)).

Каждая задача: что делаем → откуда идея → что получится → как проверим.
Статусы: `план` → `в работе` → `проверка` → `готово` / `отказ`.

## Принципы

- **Своё и компактное вместо чужого целиком.** Скиллы вызываются явно или
  с узким триггером, без хуков на каждое действие и без тысяч токенов в
  каждой сессии.
- **Проверка до включения.** Каждый скилл проходит A/B на наших реальных
  задачах (этап 0.2). Не дал прироста → не включаем.
- **Работает в облаке.** Всё должно работать в эфемерных облачных сессиях,
  а не только на локальной машине.
- **Без утечек.** Ничего клиентского во внешние сервисы, кроме того, что
  явно разрешено правилом.

---

## Этап 0. Основа

| # | Задача | Результат | Готово, когда |
|---|---|---|---|
| 0.1 | **Свой плагин в этом репозитории.** Маркетплейс `.claude-plugin/marketplace.json` и плагин `plugins/boost/`, куда складываем наши скиллы | Ставится одной командой `/plugin marketplace add tnizhnikovskyi-todo/claude_-skills` | Плагин устанавливается в облачной и локальной сессии, скилл-заглушка вызывается |
| 0.2 | **Набор задач для A/B.** `evals/`: 6–8 реальных задач (код Odoo 19, ТР, вопросы дискавери, ревью PR, исследование, поиск бага) и протокол прогона «без скилла / со скиллом» | Можно честно сравнить любой скилл | Прогнан базовый вариант «без скиллов», результаты записаны |
| 0.3 | **Шаблон `CLAUDE.md` для рабочих репозиториев** (`templates/CLAUDE.md`). Правила: «пол» качества (не добавлять `noqa`/skip, не удалять тесты, не ослаблять пороги), конвенция `shortcut: <предел>, <когда апгрейдить>`, финальная строка «что не проверено / риск», «отсутствие не доказывается поиском» | Одинаковые базовые правила во всех проектах | Шаблон применён в одном рабочем репозитории |

Источники: agent-skills (constraint-driven), ponytail, one-skill (принцип №28).

## Этап 1. Быстрые победы

| # | Задача | Результат | Готово, когда |
|---|---|---|---|
| 1.1 | **Подключить Context7.** Ключ → секрет окружения `CONTEXT7_API_KEY`, разрешить `mcp.context7.com` в сетевой политике, `.mcp.json` (или коннектор claude.ai на всю организацию). Правило в шаблон `CLAUDE.md`: в запросах только вопрос о библиотеке, для Odoo 19 `/websites/odoo/19.0`. Прочитать политику приватности | Актуальная документация Odoo 19 и библиотек в каждой сессии | A/B на 3 задачах Odoo 19: меньше устаревших API |
| 1.2 | **Скилл `interview-me`.** По одному вопросу с нашей догадкой, пересказ с разделом «Out of scope», явное «да» перед работой | Меньше работы по неверно понятой задаче | A/B на 2 расплывчатых задачах |
| 1.3 | **Скилл `source-check`** (вариант для Odoo 19). Версия → официальная документация (через Context7) → цитата; без источника пометка `UNVERIFIED` | Утверждения о API с подтверждением | Ответы на 5 вопросов Odoo 19 с цитатами, без выдуманных полей |

Источники: context7, agent-skills (interview-me, source-driven).
Зависимости: 1.3 после 1.1.

## Этап 2. Свои скиллы-усилители

| # | Задача | Результат | Готово, когда |
|---|---|---|---|
| 2.1 | **`cloud-memory`.** Память в git (`memory/` в рабочем репозитории): короткий индекс на старте через `SessionStart`-хук, полные записи по запросу; типы записей decision / bugfix / discovery; тег `<private>` не сохраняется; команды «запомни» и `handoff` (передача контекста следующей сессии в `HANDOFF.md`) | Новая облачная сессия знает решения и находки прошлых | Вторая сессия на том же репо отвечает на вопрос о прошлом решении без пересказа пользователем |
| 2.2 | **`independent-check`.** Проверка решения субагентом со свежим контекстом без наших выводов; 2–4 стратегии и судья по рубрике (арена-лайт, 1–2 раунда); каждый кандидат закрывается как `confirmed` / `ruled_out` (с названным контролем) / `open_proof_gap`; слепое сравнение с исходным ответом. Только по явной команде, агенты без права править проект | Меньше самоподтверждения на важных решениях | A/B на 3 задачах с известной ошибкой: ошибка найдена чаще, чем без скилла |
| 2.3 | **`lean-change`.** Метод ponytail: «нужно ли → есть в репо → стандартные механизмы Odoo 19 → уже установленная зависимость → минимум», без права резать валидацию и безопасность; тест на рискованную логику | Меньше лишнего кода | A/B на 3 задачах: меньше кода при той же корректности |
| 2.4 | **`repo-audit`.** Аудит репозитория целиком (ponytail-audit): переусложнения, мёртвый код, долги; находки в формате «что это / проблема / фикс / если не чинить» | Отчёт по долгам рабочего репозитория | Прогон на одном модуле Odoo, отчёт проверен вручную |

Источники: claude-mem, one-skill, graphify (2.1); agent-skills
(doubt-driven), arena-skill, strix (2.2); ponytail (2.3, 2.4).

## Этап 3. Усиление плагинов организации

Нужен доступ к репозиторию, где лежат плагины `odoo19-*`.

| # | Что меняем | Что добавляем | Источник |
|---|---|---|---|
| 3.1 | `odoo19-mvp-build:security-review` | Закрытие кандидата через counterevidence (что НЕ доказывает безопасность), калибровка severity («понижай, не удаляй»), 5 ворот проверки фикса, таблица покрытия «что проверено и чисто», скоуп PR-ревью из `diff.md`, описание PR как недоверенный ввод | strix |
| 3.2 | `odoo19-mvp-build:pr-review` | Формат находки из 4 частей, «пол» качества, мутационная проверка тестов, Prove-It (сначала падающий тест на баг), разделение старых дефектов и регрессий | ponytail, agent-skills |
| 3.3 | `odoo19-tr-authoring:tr-review` | Вызов `independent-check` для ключевых решений ТР | agent-skills, arena-skill |
| 3.4 | `odoo19-discovery-sessions:session-question-builder`, `kickoff-question-builder` | Метод `interview-me`: вопрос с догадкой, явное подтверждение, «Out of scope» | agent-skills |
| 3.5 | Все семьи плагинов (`odoo19-*`, `tr-*`) | Правило `siblings_checked`: правишь один скилл семьи, проверь соседей | one-skill |

Готово, когда: правка прошла A/B на задачах из `evals/` и принята
владельцем плагина.

## Этап 4. Внешние инструменты по требованию

| # | Задача | Условие | Готово, когда |
|---|---|---|---|
| 4.1 | **Firecrawl** hosted MCP по ключу: выключить feedback-инструменты, пиннить версию, правило «сначала WebFetch/WebSearch, Firecrawl для JS-страниц и обхода сайтов, без клиентских данных»; результаты сохранять в файлы и читать частями | Ключ (бесплатно 1000 кредитов в месяц) | A/B на 5–6 веб-задачах |
| 4.2 | **graphify** `--code-only`, ручная установка с пином, `GRAPHIFY_BACKEND=none`, свой короткий скилл на явный вызов | Ваше разрешение на запуск; сначала проверить, видит ли `_inherit` и XML-вью Odoo | Ответы о связях модулей точнее, чем через grep |
| 4.3 | **`automation-audit`**: таблица «признак репозитория → автоматизация» из claude-code-setup, плюс Odoo/Python и сверка с нашей описью | — | Аудит одного рабочего репозитория даёт рекомендации без дублей |

## Этап 5. Постоянный процесс

| # | Задача | Результат |
|---|---|---|
| 5.1 | **Наблюдения и еженедельное ревью.** Папка `observations/`: поправки пользователя и нарушения правил скиллов в формате Issue → Improvement → Principle со статусами; раз в неделю главная сессия сводит их в правки скиллов через `skill-creator`. Второе нарушение одного правила лечится барьером (хук, линт), а не новой формулировкой | Скиллы улучшаются на основе реальных ошибок |
| 5.2 | **Принципы в `criteria.md`.** Выборка из 29 starter-principles и вопросы из разборов | Строже отбор кандидатов |
| 5.3 | **Новые кандидаты:** `rtk-ai/rtk` (сжатие вывода Bash, работает в облаке), `JuliusBrussee/caveman`, `serena`, `codebase-memory-mcp` | Разбор в отдельных чатах, как раньше |

Источники: one-skill (5.1, 5.2); headroom-desktop, omniroute (5.3).

---

## Добавлено после первой волны (2026-11-02)

Из разборов `rtk`, `caveman`, `serena`, `codebase-memory-mcp` и отчётов
чатов реализации.

| # | Задача | Источник | Готово, когда |
|---|---|---|---|
| 0.4 | **Стиль ответа и формат отчётов субагентов.** Русский блок ~30 строк для шаблона `CLAUDE.md`: ответ первым, числа и отрицания неприкосновенны, явный список «когда не сжимать»; контракт для субагентов «возвращай `path:line`-таблицу, а не пересказ» | caveman (`cavecrew`) | A/B через `append_system_prompt`: короче без потери фактов |
| 0.5 | **Усложнить общий набор `evals/general/`.** Сейчас 0.98 без плагина: нужны длинный контекст, несколько ловушек, многоходовость через `history_file` | отчёт foundation | Базовая модель ниже 0.8 |
| 2.2b | **Доп. A/B `independent-check` на настоящем самоподтверждении:** модель сама пишет решение с ошибкой в прошлых ходах, потом проверяет; артефакт на несколько файлов | отчёт independent-check | Прирост > 0, иначе отказ |
| 2.5 | **Скилл `odoo-model-map`.** Карта моделей Odoo: `_name`/`_inherit` строкой, `env['…']`, `depends`, XML-вью и их наследование; «сначала оглавление, потом метод». Закрывает то, чего не видят ни graphify, ни serena, ни codebase-memory-mcp | serena, codebase-memory-mcp, graphify | На фикстурном модуле находит все наследования и вью, которые пропускает grep по классам |
| 4.4 | **Пилот rtk** (сжатие вывода Bash): OSS-сборка с пином и SHA-256, исключения для `find/cat/head/tail`, телеметрия выключена, без `rtk init`; A/B на 5–10 задачах | rtk | Экономия токенов без потерянных строк. Нужно разрешение на чужой бинарник |
| 4.5 | **Испытание codebase-memory-mcp** вместо graphify (4.2): сервер с пином, без `install` и хуков; на модуле и ядре Odoo 19 в облаке, время индексации | codebase-memory-mcp | `trace_path`/`detect_changes` полезны на Odoo. Нужно разрешение на чужой бинарник |

Отклонено во второй волне: **serena** для Odoo (LSP не видит строковый
`_inherit` и XML, `rename_symbol` опасен; вернуться для больших не-Odoo
репозиториев); рантайм **caveman** (прокси, облачный роутер, телеметрия).

## Находки третьего прохода по нашим плагинам (к исправлению)

Собираются по мере отчётов чатов анализа (2026-11-03), исправлять отдельными задачами после сбора итогов.

| # | Где | Что не так | Кто нашёл |
|---|---|---|---|
| F1 | `odoo-connector` (сервер, ~144 строки) | Нет проверок на стороне сервера: `unlink` и любой метод проходят, защита только текстом в `SKILL.md`; одна база | `analysis/erpipe-mcp-odoo` (сверено с маркетплейсом `@7acde05`) |
| F2 | `odoo19-mvp-build:code-dev`, `references/odoo-version-notes.md` | Раздел 19.0 в основном неверен: Python 3.12+/PG 16+ (в исходниках 3.10–3.14, PG ≥ 13), несуществующее `fields.AiSuggestion`, аддон `discuss` в community 19.0, совет `read_group` (deprecated в 19.0) | `analysis/unclecatvn-skills` и независимо `analysis/dooservice-odoo-skills` (сверено с `odoo@19.0`) |
| F3 | `odoo19-mvp-build:security-review` (Dimension 5) | `type='json'` — устаревший алиас в 19.0, правильно `jsonrpc` (`odoo/http.py:812–818`) | `analysis/mart337i-odoo-skills` |
| F4 | `odoo19-mvp-build:pr-review` | Ложная проверка «Odoo 19+: `mail` вместо `discuss`» — следствие ошибки F2 | `analysis/dooservice-odoo-skills` |
| F5 | `boost:odoo-model-map` (скрипт, пример в SKILL.md, фикстура, кейс `who-extends`) | В Odoo 19 `_inherit = ['x']` (список) без `_name` создаёт **новую** модель с именем из класса; расширение — только `_inherit = 'x'` строкой или явный `_name`. Наш скилл трактует список как расширение. Проверено главной сессией: `odoo/orm/models.py@19.0:240–249` против `odoo/models.py@18.0:245–250` | `analysis/odoo-lens` |

## Третий проход: что берём (план, 2026-11-03)

Источник каждой идеи — раздел «Что взять» в `catalog/<slug>/README.md` (файл@SHA, лицензия, способ). При внедрении — строка в `PROVENANCE.md`.

| # | Приоритет | Куда | Что | Источники (`catalog/…`) |
|---|---|---|---|---|
| T1 | **высокий** | `boost:source-check/references/odoo19-facts.md`, `code-dev/references/odoo-version-notes.md` | Своя таблица фактов Odoo 19 с `файл:строка` из `odoo@19.0` (вместо неверного раздела, F2); правило «одна версия, без подстраховок» | dooservice-odoo-skills, unclecatvn-skills, odoo-lens, mart337i-odoo-skills, odoo-agent-pro-kit |
| T2 | **высокий** | новый `boost:odoo19-lint` (stdlib-скрипт, опц. хук warn) | Барьер на ловушки 19: `<tree>`, `attrs=`, `type='json'`, `_sql_constraints`, `res.partner.mobile/title`, `groups_id`, `_inherit=[…]` без `_name`, `numbercall`… — у каждого правила цитата из 19.0; A/B на `general/hard` | odoo-agent-pro-kit (Apache-2.0, идея), odoo-lens (идея), F2–F5 |
| T3 | **высокий** | `odoo-connector` (маркетплейс) | Allowlist `model.method`, лимит ids, ошибка на невалидный домен, JSONL-аудит, diff «было → стало», dry-run с откатом (F1) | erpipe-mcp-odoo (MIT), dooservice-odoo-skills (`connect.md`) |
| T4 | высокий | `boost:odoo-model-map` | Исправить F5; режим «трасса от точки входа» | odoo-lens, mart337i-odoo-skills (идея), unclecatvn-skills (`odoo_trace.py`, после проверки) |
| T5 | средний | `odoo19-mvp-build:security-review`, `pr-review` | F3, F4; insecure-defaults (fail-open, `get_param(..., default)`, `verify=False`, секретное поле без `groups=`); пункты odoo-security (Markup-XSS, публичные методы = RPC, `file_open`); критерии «усугубил»; достижимость UI; differential review через `_inherit` | opencode-power-pack (идеи; CC BY-SA у ToB), dooservice-odoo-skills, security-harness, nacl |
| T6 | средний | `session-transcript-analyzer`, `meeting-protocol-builder`, анализаторы транскриптов | 5 сигналов скрытых требований и правило противоречий (→ `Q-N`, не `D-N`); проверка перепутанных меток спикеров; блок «сомнительные места» | requirement-engineer, ukr-follow-up |
| T7 | средний | `discovery-gap-analyzer`, `discovery-sow-builder`, `discovery-scope-mapper`, `handover-dossier-builder` | Конвенции gap (ID по типу, без перенумерации, тройка провенанса); «делаем / даёт клиент к сроку / не входит»; 9 содержательных проверок; чек-лист ролей стейкхолдеров | kevinlin-skills, presales-agent-skill, claude-sow-creation, ba-skills |
| T8 | средний | `tr-effort-instruction`, `preliminary-estimate` | Колонка «что делает человек», несжимаемые блоки Odoo, риск-буфер с причиной, кросс-проверка двумя методами, `stale_after` ставок, пометка аналога «до/с AI-сборкой» | ai-first-estimation, software-estimation-skills |
| T9 | средний | `tr-review`, `tr-odoo-tech-design`, `tr-usecases-acceptance` | Runtime Contract для моделей со `state`/cron; обратная трассировка журнал → ТР → SPEC → тесты (`trace-lint`); признаки неоднозначного AC | nacl, kevinlin-skills, generate-test-book |
| T10 | средний | `odoo19-sales-*` | Вставки в `loss-pattern-analyzer`/`defence-brief`/`demo-build-plan`; проблема ≠ симптом ≠ хотелка; вердикт «демо или нет»; стресс-тест экономики; статус-кво как обязательное возражение; MCQ-дозбор | lmty-skills, ai-presales-skills, mastering-technical-sales, claude-sow-creation |
| T11 | низкий | новый `uat-test-book` (`odoo19-implementation`) | UAT-таблица из AC: шаг / ожидаемое / факт / статус / роль / дефект | generate-test-book (идеи) |
| T12 | низкий | `architecture` | Линза связности аддонов Odoo (сила × расстояние × изменчивость), «не вторгаться в стандарт» | modularity (только идеи, NC) |
| T13 | низкий | `boost:cloud-memory`, `build-orchestrator` | `memory/PLAN.md` для долгих задач; `BUILD_STATE.md` на модуль | planning-with-files |
| T14 | низкий | `skill-feedback/references/weekly-review.md`, `criteria.md`, `catalog/_TEMPLATE.md` | Слияние по отложенным кейсам, no-regression по каждому кейсу, ≤4 правки за ревью; чек-лист «безопасность скилла/плагина», признаки supply-chain риска; разделы «Условия использования / Отклонённые подозрения / Что не проверено» | skillopt, repo-security-review, opencode-power-pack |
| T15 | решение пользователя | новый скилл бизнес-кейса / ROI для продаж | В `odoo19-sales-*` ROI нет | ba-skills |

## Четвёртый проход: что берём (план, 2026-11-03)

Источник: `catalog/INDEX.md` («Четвёртый проход»), 22 разбора. Ни один инструмент не ставим.

| # | Приоритет | Куда | Что | Источники |
|---|---|---|---|---|
| U1 | высокий, в работе | `odoo-connector` | второй круг T3 (см. статус T3) | odoo-mcp-19, mcp-server-odoo, odoo-functional-agent |
| U2 | высокий, в работе | `boost:odoo19-lint`, `odoo-version-notes.md` | второй круг T1/T2; правило «у факта две ссылки: N-1 и N» | panus-odoo-dev-skill, odoo-migrate-to-20, odoo-spec-kit |
| U3 | высокий | `plugins/boost/evals/README.md`, `weekly-review.md` | правила A/B: табло активации, «задача соседа», контроль без скилла не перезапускать, шум вне знаменателя, шапка окружения; парное A/B старой и новой версии; leave-one-out; правило принятия Δ > 0.05; лимит роста `SKILL.md`; кейс «конкурирующий промпт». Пометить +0.11 (`odoo-model-map`) и +0.23 (`repo-audit`) как «в пределах шума» или перепроверить `--runs 5`. Связать с T14 | caliper (`catalog/caliper/evals-rules-draft.md`), upskill, darwin-skill, ecc |
| U4 | высокий | новый `scripts/skill-prescan.py` + шаг −1 сессий анализа + проверка перед публикацией в маркетплейс | stdlib-префильтр (Semia: 20/21 вредоносов → BLOCK, 0 ложных на `boost`), регулярки `security.sh` (MIT) + рус./укр. фразы, хуки/MCP/`allowed-tools`, tag-символы; дубли триггеров по Unicode-Jaccard; лимит описания 1 536 | semia (`items/skill_prescan.py`), skills-janitor, repo-security-review |
| U5 | высокий | T5: `security-review`, `pr-review` | 12 вопросов Access control / Business logic для Odoo; различитель high/medium; барьер «каждая строка диффа с `route`/`sudo()`/`cr.execute`/ACL — в таблице покрытия»; Gate Integrity; карточка ценности теста; сверка scope ТР/SPEC с диффом | cloudflare-security-audit, gstack, ecc, claude-sdlc-skills |
| U6 | средний | `sale_todo_claude`: `scripts/check-humizer.py`, `shared/registers.md` §3/§7 | бот-хвосты (блок), чужие буквы/невидимые символы, ~25 русизмов, кальки, канцелярит (предупреждения); чистые фикстуры из реальных КП. Апостроф — `ʼ` (U+02BC), решение пользователя 2026-11-03; «блокуючий» → «блокувальний» | humanizer-uk, anti-ai-slop-writing |
| U7 | средний | T11 `uat-test-book`; `testing`, `acceptance-act-builder`, `hypercare-tracker` | статусы строки UAT, матрица AC → кейсы → пробел, fail-closed критерии выхода, «Test plan / Not tested», роли без админ-групп; доказательство установки (rc 0, `state='installed'`, HttpCase реально шли) | awesome-qa-skills (только идеи, PolyForm NC), odoo-functional-agent, odoo-migrate-to-20 |
| U8 | средний | дискавери и ТР: `kickoff-question-builder`, `demo-debrief`, `tr-review`, `tr-usecases-acceptance`, журнал дискавери, `boost:interview-me` | «Розвідка» (`blindspot-pass`) перед вопросами; «вкус показывают» (3–5 вариантов); блок «Повнота» в `tr-review`; AC «Не повинно» и «Перевірка: метод»; G1–G4 сохранения по `state`; реестр «термин клиента → объект Odoo»; 4 правила в `interview-me` | finding-unknowns, claude-sdlc-skills, ecc |
| U9 | средний | продажи: `defence-brief`, `presale-pack-builder`, `offer-finalizer`, `demo-runbook` (с T10) | измерения закупки (референсы, SLA, хостинг, рост цены лицензий, устойчивость интегратора), «як це побачить клієнт», банк вопросов покупателя | buyer-eval (`items/buyer-diligence-questions.md`) |
| U10 | средний | `boost:skill-feedback`, `cloud-memory` | промпты извлечения правила (триггер = ситуация, тест тавтологии, расширенные сигналы поправки, формат пути успеха); `confidence`, общее правило только при повторе в 2+ проектах | claude-smart, ecc |
| U11 | низкий | `odoo-connector` | JSON-2 вторым транспортом по версии (XML-RPC в 19 deprecated, удаление в 22); после U1 | odoo-mcp-19, mcp-server-odoo |
| U12 | низкий, после A/B | `boost:debug-root-cause`; правила `boost` | стоп после 3 гипотез, DEBUG REPORT, blast radius; «лестница правки» против разбухания скиллов | gstack (pstack, skill-diet — разобрать первоисточники) |
| U13 | высокий, действие пользователя | claude.ai → навыки аккаунта/организации | Разобрано главной сессией: см. `decisions/2026-11-03-old-skill-copies.md`. 10 старых копий скиллов (май–июль 2026, `source: plugin`) дублируют имена и триггеры скиллов плагинов `odoo19-*`; оставить версии плагинов, копии отключить. Префильтр нашёл ещё пару: `brief-transcript-analyzer` (продажи) ↔ старая копия `session-transcript-analyzer` (у копии нет границы «НЕ для брифу») | skills-janitor, главная сессия |

## Решения владельца 2026-11-04 (бывшие открытые вопросы)

| Вопрос | Решение | Где делается |
|---|---|---|
| Пороги продаж (`stale_after` ставки, ставка сейла, кросс-проверка) | оставить: полгода / 6 мес. / 30% | — |
| Humizer: блок сразу или мягкий старт | до 2026-11-18 предупреждать, с 2026-11-19 блокировать | [сессия](https://claude.ai/code/session_01L4X5dwKG29a3ycfAg8iDAp), `claude/humizer-warn-email` в sale_todo_claude |
| Humizer для писем | сделать `--channel email`, подключить к `demo-followup-writer` | там же |
| ROI-скилл (T15) | пока нет | — |
| ИИ-ускорение в оценке ТР | не учитывать (часы без скидки) | [сессия](https://claude.ai/code/session_01L4X5dwwg1tycz1vYDxRxfW), `claude/tr-pm-share` в маркетплейсе |
| Доля PM в оценке ТР | добавить, 10% | там же |
| Срок в протоколе без договорённости | только из стенограммы, иначе «термін не визначено» + открытый вопрос | там же (`meeting-protocol-builder`) |
| odoo-ls вторым слоем к линтеру | разрешено: сборка официального `odoo-ls` и A/B, лимит $5 | [сессия](https://claude.ai/code/session_01L4X5dwiM5PUk6JgMfnF1P1), `build/odoo-ls-layer` |
| `memory/PLAN.md`: отдельная проверка на прерванной задаче | не нужна: A/B `cloud-memory/long-plan` 3/3 | — |

## Что нужно от пользователя

| Решение | Для задач | Вариант по умолчанию |
|---|---|---|
| Где живут наши скиллы | 0.1, этап 2 | Плагин в этом репозитории |
| Ключ Context7 и способ подключения | 1.1, 1.3 | Ключ в секреты окружения; позже коннектор на организацию |
| Доступ к репозиторию плагинов `odoo19-*` | этап 3 | Предложить правки как PR владельцу |
| Ключ Firecrawl | 4.1 | Отложить до этапа 4 |
| Разрешение запускать graphify | 4.2 | Отложить до этапа 4 |
| Рабочий репозиторий для пилота | 0.2, 0.3, 2.1, 2.4 | Один небольшой Odoo-проект |

## Как будем работать

Как с анализом: каждая задача (или связка, например 1.2 + 1.3) идёт
отдельным чатом в ветке `build/<slug>`. Главный чат ставит задачу, сводит
результаты, ведёт статусы в этом файле.

| # | Статус | Чат | Ветка | Отчёт |
|---|---|---|---|---|
| 0.1 | готово | главная сессия | | |
| 0.2 | готово (набор упирается в потолок → 0.5) | [foundation](https://claude.ai/code/session_01L4X5e1XU6o9G3qUruKMTMn) | `build/foundation` | `reports/foundation.md` |
| 0.3 | готово: шаблон применён в `pilot/CLAUDE.md`; в пилоте его правила соблюдались в обоих плечах | главная сессия | | `pilot-notes/README.md` |
| 0.4 | готово: компактный раздел «Стиль и субагенты» в `templates/CLAUDE.md` (одна строка −27% длины без потери фактов; полный блок `templates/CLAUDE-style.md` не включён) | foundation | `build/foundation` | `reports/foundation.md` |
| 0.5 | готово: уровень `hard` 0.755 без плагина (цель < 0.8); база ошибается только на фактах Odoo 19 | foundation | | |
| 1.1 | ждёт ключ Context7; инструкция и `templates/mcp.json` готовы | foundation | | `templates/README.md` |
| 1.2 | готово, в плагине | [interview-source](https://claude.ai/code/session_01L4X5dxWNHTCxZX6YvcL6a7) | `build/interview-source` | `reports/interview-source.md` |
| 1.3 | готово, в плагине; повторить A/B с Context7 после 1.1 | interview-source | | |
| 2.1 | готово, в плагине; пилот на рабочем репозитории | [cloud-memory](https://claude.ai/code/session_01L4X5dzUi82gav7qHcVBeNe) | `build/cloud-memory` | `reports/cloud-memory.md` |
| 2.2 / 2.2b | **отказ**: Δ = 0 на 8 кейсах (вкл. самопроверку через историю), в 4–5 раз дороже | [independent-check](https://claude.ai/code/session_01L4X5dyQd2f4Mh8gpmeyMcM) | `build/independent-check` (архив, не слита) | `reports/independent-check.md` |
| 2.3 | готово, в плагине | [lean](https://claude.ai/code/session_01L4X5dxJQwq1GhZzTZqZuEh) | `build/lean` | `reports/lean.md` |
| 2.4 | готово, в плагине; прогон на рабочем модуле Odoo | lean | | |
| 2.5 | готово, в плагине (+0.11); прогон на ядре Odoo 19 и рабочем модуле | [odoo-model-map](https://claude.ai/code/session_01L4X5dxEu7FH3tN8TH8JSfr) | `build/odoo-model-map` | `reports/odoo-model-map.md` |
| 3.1 | проверка: предложение готово (15/15 против 13.5/15 на фикстурах) | [review-upgrades](https://claude.ai/code/session_01L4X5dxM8fDnFXcEC1bqyAj) | `build/review-upgrades` | `proposals/odoo19-mvp-build/README.md` |
| 3.1, 3.2, 3.4, 3.5 | готово: влито в main `todoltd/claude-methodology-marketplace` (merge `e4c70d8`, отчёт `8e97644`), подтверждено владельцем; осталось перенести правки в локальную папку «Методологія ToDo+AI», откуда берёт исходники `sync-marketplace.sh` | [boost-proposals](https://claude.ai/code/session_01L4X5dziDUMxUkdQ1zXJ1Pf) | | `BOOST_PROPOSALS_REPORT.md` |
| 3.2 | проверка: вставка готова (10/10 против 8/10); текст `pr-review` не найден в окружении | review-upgrades | | |
| 3.3 | отменена (2.2 отказ); блок «что НЕ доказывает корректность» уже входит в предложение 3.1 | | | |
| 3.4 | проверка: предложение готово (гипотезы к вопросам 0% → 87–100%, склейки ~30–40 → 0–3); оригиналы скиллов не найдены, проверено на заменителях | [discovery-interview](https://claude.ai/code/session_01L4X5dxFcHE2T9drn8GJzP1) | `build/discovery-interview` | `proposals/odoo19-discovery/README.md` |
| 3.5 | проверка: предложение и карта соседей готовы | главная сессия | | `proposals/siblings-checked.md` |
| 4.1 | ждёт ключ Firecrawl | | | |
| 4.2 | заменено на 4.5 | | | |
| 4.3 | готово, в плагине (+0.36) | [automation-audit](https://claude.ai/code/session_01L4X5e1ZugnciMyW7EMAugR) | `build/automation-audit` | `reports/automation-audit.md` |
| 4.4 | отложено: база 18/18, вывод Bash ≈ 2.7% входа → потолок экономии 1–3%; 3 из 6 ловушек в зоне урезания rtk; плечо rtk не запущено (блок классификатора) | [rtk-pilot](https://claude.ai/code/session_01L4X5e1jKV3A2wTSXnx6WP4) | `build/rtk-pilot` | `reports/rtk-pilot.md` |
| 4.5 | отложено: без MCP 28.5/29, с `boost` 29/29; граф по исходникам не моделирует строковый `_inherit`, XML и права; ~5.7k токенов схем; запуск бинарника заблокирован | [cbm-pilot](https://claude.ai/code/session_01L4X5dy4DhWq69JxUWuSYwo) | `build/cbm-pilot` | `reports/cbm-pilot.md` |
| 5.1 | готово, в плагине (+0.45); 5 наблюдений в `observations/`; еженедельная задача не создана, промпт готов | [observations](https://claude.ai/code/session_01L4X5dwJimwjr7KpRxJq5ja) | `build/observations` | `reports/observations.md` |
| 5.2 | готово: принципы в `criteria.md` | главная сессия | | |
| 5.3 | готово: 4 разбора слиты | см. `sessions.md` | | `catalog/INDEX.md` |
| пилот | готово: `pilot/` (Odoo 19, 3 модуля) + `pilot-notes/`; находки плагина ≈ базе, плагин даёт форму, шаблон CLAUDE.md даёт дисциплину | главная сессия | | `pilot-notes/README.md` |
| лицензия | готово: MIT (`LICENSE`, `plugins/boost/LICENSE`, `plugin.json`) | главная сессия | | |
| чек-лист repo-audit | готово: пункты про `ir.rule` дочерних моделей и пустые группы (из пилота: K12, K15) | главная сессия | | |
| 5.1 расписание | готово: задача по расписанию «Еженедельный разбор замечаний к скиллам», пн 10:40 по Киеву, первый запуск 2026-11-09; только предлагает решения, правки после одобрения | главная сессия | | |
| перенос в локальную папку | готово 2026-11-03: коммит `e0977ed` в монорепо (ветка `feat/bi-dashboards`) — ровно 21 файл; посторонние файлы снова незакоммичены; PR #7 закрыт; локальный клон маркетплейса на `8e97644`, `--gated --dry-run`: все плагины «без змін» | главная сессия | | |
| доставка сотрудникам | готово 2026-11-03: PR #8 влит (`9e19e33`); организация подхватила: в синхронизированных плагинах `boost` 0.4.0 (8 скиллов), `odoo19-mvp-build` 0.9.1, `odoo19-discovery-sessions` 0.6.0, `odoo19-discovery-initiation` 0.11.0; скиллы доступны в новой сессии | главная сессия | | |
| предупреждения синка claude.ai | готово 2026-11-03: `boost` 0.4.1 (#9); продажи 0.4.1 без `$schema`/`defaultEnabled` + накопленные правки (#10, `7acde05`); пользователь включил право Actions открывать PR | главная сессия | | |
| T1 | готово, [PR #11](https://github.com/todoltd/claude-methodology-marketplace/pull/11) не слит: `odoo19-mvp-build` 0.9.3, таблица фактов с двумя ссылками 18.0/19.0 (R1–R5, M1–M18, B1–B8, V1–V5…), M12 — ошибка, CRLF сохранён
| T2 | готово, слито в хаб: 40 правил (31 ERROR, 9 WARN), сверены с 19.0 и 18.0; A/B: кейсы +0.30, `general/hard` 0.755 → 1.00, второй круг +0.73; на Odoo 19.0 0 ERROR; $6.56 за оба круга. Ждёт публикации `boost` | [T2](https://claude.ai/code/session_01L4X5dyWpMXotVz4BwTqWyE) | `build/odoo19-lint` | `reports/odoo19-lint.md` |
| T3 | готово, [PR #12](https://github.com/todoltd/claude-methodology-marketplace/pull/12) не слит: `odoo-connector` 0.2.1, 57 тестов (хаб перепроверил: OK); блок-листы моделей и методов, x2many/`default_*`/`load`/`copy`, `unlink` ≤ 1, `expected_marker` (для не-админа всегда блок: `get_param` требует `group_system`). Открыто: бизнес-методы, меняющие другие модели; лимит для методов по домену; elicitation
| T4 | готово, слито в хаб: F5 исправлен + режим «трасса от точки входа», 17 тестов, Δ +0.22 ($3.5); ждёт публикации вместе с T2 | [T4](https://claude.ai/code/session_01L4X5dxi7y9ihHDLZzemase) | `build/odoo-model-map-f5` | `reports/odoo-model-map-f5.md` |
| U3… | готово, слито в хаб: «Методика A/B» в `evals/README.md`, еженедельное ревью с парным A/B, `skill-feedback` (+0.41) и `cloud-memory` (8/8 против 3/8, `memory/PLAN.md`), чек-лист безопасности в `criteria.md` и разделы `_TEMPLATE.md`. Перепроверка `--runs 5`: `odoo-model-map` и `repo-audit` устойчивы на своих сильных кейсах. ≈ $25. Осталось: хук `memory-start.sh` подмешивает открытый `memory/PLAN.md` (отдельно, с проверкой цены старта): U3, T14, U10, T13 (память) | [eval-feedback-loop](https://claude.ai/code/session_01L4X5dz8s2fhuggS3wZ24VC) | `build/eval-feedback-loop` | `reports/eval-feedback-loop.md` |
| U4… | готово, слито в хаб: `scripts/skill-prescan.py`, 15/15 вредных → BLOCK, 0 ложных на 4 чистых наборах; шаг −1 в `CLAUDE.md`, барьер перед публикацией `boost`; осталось: CI маркетплейса, копия в `sale_todo_claude/scripts/`, ссылка в `criteria.md` (после `eval-feedback-loop`); детектор дублей считает фразы из негативной границы «НЕ для…» триггерами (ложный WARN `debug-root-cause` ↔ `interview-me` на «как работает X») — исключить; `curl | sh` внутри `echo`-подсказки (`odoo-connector/server/run.sh:15`) даёт BLOCK, а «без запису» о preview — WARN claim-vs-behavior: учитывать контекст строки: U4 | [skill-prescan](https://claude.ai/code/session_01L4X5e1uX9yvXTuHu8Bd2TE) | `build/skill-prescan` | `reports/skill-prescan.md` |
| U8… | в работе: U8 (`interview-me`), U12, `source-check`, `repo-audit` | [boost-pass4](https://claude.ai/code/session_01L4X5e17u1jqRvjUEg5tw9x) | `build/boost-pass4` | `reports/boost-pass4.md` |
| T5/U5… | готово (`odoo19-mvp-build` 0.9.4 поверх T1): 12 вопросов атаки, стоки и insecure-defaults, барьер покрытия, Gate Integrity, карточка ценности теста, G1–G4, `BUILD_STATE.md`. A/B 5 кейсов: 16/16 и 11/11 в обоих плечах — по находкам потолок, плюс только в полноте отчёта, +4–13% токенов: T5/U5, T12, T13 (`build-orchestrator`) | [mvp-build-pass4](https://claude.ai/code/session_01L4X5dzzKrTbWWy1jgXLDPm) | `claude/mvp-build-pass4` в маркетплейсе (от T1) | `MVP_BUILD_PASS4_REPORT.md` |
| T6… | готово (initiation 0.12.0, sessions 0.7.0, closeout 0.5.0; реестр терминов `L-N`). A/B: C1 транскрипт — скрытые требования 4/4 против 1/4, сомнительное число не записано фактом; C2 вопросы УЗ — паритет 5/8; закрытие (T7) не прогонялось. Доп. шаг: правило «міна → питання №N або „не питаємо, бо...“»; повтор C2 на 3 брифах — темы 15 → 16 из 24, висячих мін 0 из 20, показ вариантов 0 → 3; прироста экспертных вопросов почти нет. Дальше: отраслевой чек-лист мін как вход; C3 (закрытие) не прогонялся: T6, T7, U8 (дискавери) | [discovery-pass4](https://claude.ai/code/session_01L4X5dwunfS1yoyCvLRQ2B3) | `claude/discovery-pass4` в маркетплейсе | `DISCOVERY_PASS4_REPORT.md` |
| T9… | готово (`odoo19-tr-authoring` 0.7.0): «Повнота» П1–П7, AC «Не повинно / Перевірка», G1–G4, Runtime Contract, `trace_lint.py`, T8 в `tr-effort-instruction`. A/B 3 синтетических ТР: ключей 15/15 против 11/15, 0 ложных 🔴 против 1, ×1.7 (n=1, ключи закладывал автор). Нужно: `spec-writer` должен знать раздел «Допущення…» (правка в `odoo19-mvp-build`); BA подтверждает `stale_after` и «до AI» у старых ставок: T9, U8 (ТР), T8 (`tr-effort-instruction`) | [tr-pass4](https://claude.ai/code/session_01L4X5dwkPrjvzommx6kdtyU) | `claude/tr-pass4` в маркетплейсе | `TR_PASS4_REPORT.md` |
| T11… | готово (`odoo19-implementation` 0.3.0, новый `uat-test-book`, fail-closed приёмка; A/B 2 набора: без скилла 29–33 внутренних ID в тексте для клиента, админ в тест-ролях, нет Test plan; со скиллом всё закрыто). При слиянии: правка `track-convergence` поднимает `odoo19-mvp-build` до 0.9.2, а T1 уже 0.9.3 — переставить версию после T1: T11, U7 | [uat-test-book](https://claude.ai/code/session_01L4X5dyiW4w5HTW2Qi9cKwg) | `claude/uat-test-book` в маркетплейсе | `UAT_TEST_BOOK_REPORT.md` |
| U6… | готово, [PR #2](https://github.com/tnizhnikovskyi-todo/sale_todo_claude/pull/2) в sale_todo_claude не слит: `check-humizer.py` блокирует чужие буквы, невидимые символы, апостроф не `ʼ`, 25 русизмов, 19 причастий, бот-хвосты; предупреждает о кальках, канцелярите, штампах; 1158 автокейсов + мутационный тест (18 мутаций); на `shared/examples` 42 новых срабатывания, все верные. Открыто: `demo-followup-writer` не вызывает чекер; 12 «блокуючий» в SKILL.md шести скиллов (после sales-pass4); режим `--channel email` — решение владельца: U6 (апостроф `ʼ`) | [humizer-uk-pass4](https://claude.ai/code/session_01L4X5e1uPxnWnBvhELUGDuz) | `claude/humizer-uk-pass4` в sale_todo_claude | `HUMIZER_PASS4_REPORT.md` |
| T10… | готово (`odoo19-sales-*` 0.5.0, ветка `claude/sales-pass4`): `shared/buyer_diligence.md` и проверка покрытия в pre-save, `defence-brief` («як це побачить клієнт», статус-кво, «що клієнт знайде сам»), вердикт демо в `demo-build-plan`, стресс-тест в `offer-finalizer`, MCQ-дозбор, несжимаемые блоки и `stale_after` в `preliminary-estimate`. A/B 3 синтетические сделки: 3.5→5/5, 3→5/5, 1.5→4/4 (ловушки под новые правила, n=1). Решение владельца: `stale_after` ставки (полгода), срок ставки сейла (6 мес.), порог кросс-проверки (30%). Найдены разрывы: `client-followup-writer` не читает `повнота_даних`, `defence-brief` не читает `аналіз_втрат`: T10, U9, T8 (`preliminary-estimate`) | [sales-pass4](https://claude.ai/code/session_01L4X5dyMPpMfQehWMCwG9RD) | `claude/sales-pass4` в sale_todo_claude | `SALES_PASS4_REPORT.md` |
| Выпуск 2026-11-03 | **слито 2026-11-04**: [PR #13](https://github.com/todoltd/claude-methodology-marketplace/pull/13) и #12 в маркетплейс (`206bb33`), продажи #2 и #3 (`6c4b4af`); синк продаж 0.5.0 — [PR #14](https://github.com/todoltd/claude-methodology-marketplace/pull/14) слит 2026-11-04 (`ccdc774`; PR открыт вручную — у Actions снова нет права открывать PR); #11 открыт, но уже в `main` — закрыть; монорепо: 95 файлов выпуска применены и закоммичены владельцем 2026-11-04 (`7d36d04` в `feat/bi-dashboards`, вместе с 19 его собственными правками — 114 файлов); пуш монорепо ждёт нового приватного репозитория. Было: T1, T3, mvp-build-pass4, uat-test-book, discovery-pass4, tr-pass4, `boost` 0.5.0; продажи — [PR #2](https://github.com/tnizhnikovskyi-todo/sale_todo_claude/pull/2) (Humizer), затем [PR #3](https://github.com/tnizhnikovskyi-todo/sale_todo_claude/pull/3). После слияния: архив для монорепо, архив сессий | главная сессия | | |
| U11, T15 | ждут: JSON-2 — после T3; ROI-скилл — решение пользователя | | | |
