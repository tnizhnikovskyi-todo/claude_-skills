# ECC (бывший everything-claude-code)

- **Тип:** плагин-сборник (скиллы, агенты, команды, хуки, правила, установщик, свой CLI `ecc`, `ecc2` на Rust, дашборд)
- **Источник:** https://github.com/affaan-m/ECC
- **Версия / коммит:** 2.2.3, `b38be6a7f6350964d59328b52f0624e1d1d552d1` (2026-10-29)
- **Лицензия:** MIT (© 2026 Affaan Mustafa) по файлу `LICENSE`; исключения: `skills/osint-investigation` — CC BY-SA 4.0, 8 скиллов логистики/производства — Apache-2.0 (frontmatter `license:`), `skills/context-and-decisions` — MIT © Matt Pocock
- **Дата разбора:** 2026-11-03
- **Вердикт:** **отклонить установку; адаптировать 6 небольших вставок** (итог как плагина 7/18)

## Что делает

«Операционная система для харнесса агента»: 314 скиллов, 71 агент,
98 команд, 28 регистраций хуков на 9 событий, правила для 20 языков,
установщик с профилями (`minimal` … `full`), кросс-харнесс (Claude Code,
Codex, Cursor, OpenCode, Gemini, Kiro, Qwen и др.). Скиллы почти все под
веб-разработку (TS/React/Django/Spring/Go/Rust), плюс маркетинг, трейдинг,
логистика, homelab. Про Odoo нет ничего (поиск по `skills/ agents/ rules/
commands/` — 0 совпадений; прочитан список всех 314 имён).

## Популярность: настоящая ли

296 302 ★ и 43 824 форка за 10 месяцев (создан 2026-01-18). Признаков
накрутки нет: 4321 коммит, 517 авторов, 1345 слитых PR, 940 issues с
содержательными багами; форков ≈15% от звёзд (у купленных звёзд форков
почти нет). Это вирусная популярность «набора всего для Claude Code», а не
показатель пользы для нас: 2 автора делают ~60% коммитов, много мусорных
issues «[Copilot]» — аудитория широкая и случайная. Список поставивших звёзды через API
проверить не смогли (у сессии нет доступа к API этого репозитория). Подробно:
`notes.md`.

## Маркетинг и что реально меняет поведение

| Заявлено | Что на деле |
|---|---|
| «Agent harness OS», 314 скиллов | 90% — справочники фреймворков, которые модель и так знает; к Odoo/БА/продажам относятся единицы |
| «Инстинкты», continuous learning | Захват всех вызовов инструментов на диск + фоновый Haiku, по умолчанию выключен; см. `items/continuous-learning-v2.md` |
| «Безопасность» | `gateguard`, `config-protection` — настоящие барьеры-хуки; `security-review`/агенты — чек-листы, дублируют встроенный `security-review` |
| «Research-first» | `search-first`/`deep-research` — процесс, который модель делает по прямой просьбе; Firecrawl/Exa по ключу |
| «A/B-tested +2.25» (gateguard) | 2 задачи автора, рубрика не опубликована |
| Спонсорские вставки | `scripts/lib/compute-sponsor.js` (Itô GPU), `nasiko-release.js`, приветствие в терминале со ссылками на Discord/GitHub App |

Реально меняют поведение (и разобраны в `items/`): хуки-барьеры
(gateguard, config-protection), формат записи наблюдений (инстинкты),
формат AC (intent-driven), глоссарий домена (context-and-decisions),
метод проверки соблюдения скилла (skill-comply), сверка плана с диффом
(change-impact).

## Always-on: что работает в каждой сессии и сколько стоит

Оценка по исходникам (символы / 4 ≈ токены), не по замеру `/context`.

| Что | Когда | Стоимость |
|---|---|---|
| Описания 314 скиллов | каждая сессия при включённом плагине | 102 тыс. символов ≈ **25.6 тыс. токенов**; Claude Code режет листинг по бюджету, значит часть описаний просто не видна — триггеры ненадёжны |
| Описания 71 агента | каждая сессия | ≈ 4 тыс. токенов |
| Описания 98 команд | каждая сессия | ≈ 3.5 тыс. токенов |
| Правила `rules/common` (+ `python`) | каждая сессия, если ставить установщиком в `~/.claude/rules` | 19.4 + 4.8 КБ ≈ 6 тыс. токенов; содержимое — общие места («валидируй ввод», «80% покрытия») |
| `SessionStart` | старт | до 8000 символов ≈ 2 тыс. токенов (прошлые сессии, до 6 инстинктов) |
| Хуки `PreToolUse`/`PostToolUse` | каждый вызов инструмента | Bash: ~6 запусков node; Edit/Write: ~8 (gateguard, config-protection, suggest-compact, observe, governance, hookify + 2 PostToolUse). Токенов мало, но задержка и 2750+ строк чужого JS на каждый шаг |
| gateguard | первая правка каждого файла, каждая разрушительная команда | лишний ход модели с ответом на 3–5 вопросов |
| `Stop` | после каждого ответа | 8 хуков: форматирование/tsc (до 300 с), console.log, сохранение сессии, оценка сессии, учёт стоимости, уведомление |

Итого **≈ 33 тыс. токенов описаний в каждой сессии** только от плагина
(у gstack ~5.5 тыс. на вызов, у opencode-power-pack 3.6 тыс., у
agent-skills 3–4 тыс.) + хуки на каждый шаг. Для нас — однозначный минус
(`synthesis.md`, п. 5; `criteria.md`, «Цена контекста»).

## Безопасность, сеть, что ставится

- Прочитаны: `hooks/hooks.json`, `hooks/hooks.metadata.json`,
  `scripts/hooks/{config-protection,session-start,insaits-security-wrapper}.js`,
  фрагменты `gateguard-fact-force.js`, `skills/continuous-learning-v2/hooks/observe.sh`,
  `install.sh`, `.mcp.json`, `.claude-plugin/*.json`. Ничего не запускали.
- **Сеть из хуков:** не найдено внешних URL и `fetch`/`npm`/`curl` в
  `scripts/hooks/*.js` (только `http.request` на локальный Plan Canvas).
  Телеметрия локальная: `~/.claude/metrics/costs.jsonl`, skill-health.
  `governance-capture` и InsAIts (Python-монитор) — только по флагу
  `ECC_GOVERNANCE_CAPTURE=1` / `ECC_ENABLE_INSAITS=1`.
- **На диск:** `observe.sh` по умолчанию пишет вход/выход каждого
  инструмента (до 5000 символов) в `~/.local/share/ecc-homunculus/`, с
  регулярками против секретов, которые известно пропускают голые ключи
  (issue 2026-11-03). Для нас это данные клиентов из Odoo/Gmail/Fathom.
- **`.mcp.json`** в корне: `npx -y chrome-devtools-mcp@1.10.1` (версия
  закреплена). В `plugin.json` стоит `mcpServers: {}`; поднимется ли сервер
  при установке плагина — не проверяли.
- **Установщик** `install.sh` → `npm install --ignore-scripts` →
  `scripts/install-apply.js` пишет в `~/.claude/` (правила, агенты,
  команды, хуки в `settings.json`).
- Слабые места из свежих issues: gateguard обходится правкой
  `.claude/settings*.json`, сообщения об отказе подсказывают агенту, как
  отключить проверку.

## Сравнение с нашим

| У них | У нас | Итог |
|---|---|---|
| `code-reviewer`, `security-reviewer`, 20+ языковых ревьюеров, `verification-loop` | встроенные `code-review`/`simplify`/`security-review`, `odoo19-mvp-build:pr-review`/`security-review` | дубль |
| `santa-method`, `council` | `independent-check` отклонён (Δ = 0) | дубль отклонённого |
| `search-first`, `deep-research` | `lean-change`, `source-check`, Context7 | дубль; deep-research требует Firecrawl/Exa |
| `continuous-learning-v2`, `unified-memory`, сессии в `~/.claude` | `skill-feedback` + `observations/`, `cloud-memory` (git) | у нас лучше для облака; берём 2 идеи формата |
| `gateguard`, `config-protection` | «Пол качества» текстом в `templates/CLAUDE.md` | у них барьер; берём идеи, хук — только после 2-го нарушения |
| `skill-comply`, `skill-stocktake` | `evals/`, `claude plugin eval`, `automation-audit` | у них есть кейс «конкурирующий промпт» — берём |
| `intent-driven-development` | `interview-me`, `tr-usecases-acceptance` | у них строки Must not / Verification — берём |
| `context-and-decisions` | реестры журнала дискавери D/X/C/T/Q/A | у них глоссарий — берём |
| `strategic-compact`, `context-budget` | встроенные `/context`, автокомпакт | не нужно |
| `lead-intelligence`, `market-research`, `competitive-report-structure`, `investor-*` | `odoo19-sales-*` | у них X API/Exa и стартап-фандрайзинг, нам не подходит |
| Сравнение с соседями | gstack (10/18, 5.5 тыс. токенов на вызов), opencode-power-pack (8/18), agent-skills (не ставить) | ECC самый дорогой из разобранных |

## Сводная таблица компонентов

| Компонент | Карточка | Always-on | Итог | Вердикт |
|---|---|---|---|---|
| `gateguard` (хук + скилл) | `items/gateguard.md` | да, каждый Edit/Write/Bash | 9/18 | адаптировать идею |
| `continuous-learning-v2` | `items/continuous-learning-v2.md` | да, каждый вызов | 9/18 | отклонить, 2 идеи |
| `config-protection` (хук) | `items/config-protection.md` | да, Edit/Write | 14/18 | адаптировать (свой хук по необходимости) |
| `skill-comply` | `items/skill-comply.md` | нет | 13/18 | адаптировать идею в эвалы |
| `intent-driven-development` | `items/intent-driven-development.md` | нет | 15/18 | адаптировать 2 строки AC |
| `context-and-decisions` | `items/context-and-decisions.md` | нет | 15/18 | адаптировать (глоссарий G-N) |
| `search-first` / `deep-research` / `change-impact` | `items/research-first.md` | нет | 12/18 | 1 вставка в `pr-review` |
| `santa-method` / `council` | `items/santa-method-council.md` | нет | 10/18 | отклонить |

## Проверка

| Задача | Без него | С ним |
|---|---|---|
| — | A/B не делали: запрет на запуск чужого кода; вставки текстовые, их проверять в сессиях реализации | — |

## Оценка (плагин целиком)

| Критерий | Балл (0–3) | Комментарий |
|---|---|---|
| Прирост | 1 | 6 полезных вставок из ~480 файлов-инструкций; остальное модель умеет сама или не про нас |
| Частота | 1 | Нашей работы (Odoo, БА, продажи) почти не касается |
| Надёжность | 1 | 314 описаний не помещаются в бюджет листинга; хуки ломаются на Windows (issues) |
| Стоимость контекста | 0 | ≈33 тыс. токенов в каждой сессии + хуки на каждый шаг |
| Безопасность | 2 | Сети из хуков нет, телеметрия локальная; но сырые данные инструментов пишутся на диск, огромная поверхность чужого JS |
| Поддержка | 2 | Очень активен (955 коммитов в октябре), но 2 автора, вирусная аудитория |
| **Итого** | **7/18** | |

## Что взять

Все шесть — пересказ своими словами; лицензия MIT позволяет и дословно, но
текст у нас свой и по-русски/по-украински. Атрибуция — в
`references/attribution.md` (`ATTRIBUTION.md`) целевого скилла.

| # | Исходный файл (`путь@SHA`) | Что берём | Куда у нас | Как | Лицензия |
|---|---|---|---|---|---|
| 1 | `skills/intent-driven-development/SKILL.md@b38be6a` (шаблон AC, стр. 278–279) | Строки AC «Не повинно (Must not)» и «Перевірка: метод/доказательство» | `odoo19-tr-authoring:tr-usecases-acceptance` + пункт в `tr-review` | пересказ | MIT ✔ |
| 2 | `skills/context-and-decisions/SKILL.md@b38be6a`, `templates/context.example.md` | Реестр `G-N` «термины клиента → значение → объект Odoo → источник», раздел «требует подтверждения» | `odoo19-discovery-sessions:session-transcript-analyzer` (журнал) | пересказ, атрибуция **Matt Pocock** | MIT ✔ |
| 3 | `skills/skill-comply/prompts/scenario_generator.md@b38be6a` | Эвал-кейс «конкурирующий промпт» для скиллов, меняющих действие | `plugins/boost/evals/README.md` | идея | MIT ✔ |
| 4 | `skills/continuous-learning-v2/SKILL.md@b38be6a` («The Instinct Model», «Promotion») | `confidence` + доказательства у записи; в общее правило — только при повторе в 2+ проектах | `plugins/boost/skills/skill-feedback` | идея | MIT ✔ |
| 5 | `skills/gateguard/SKILL.md@b38be6a` («Questions by target class», «Destructive Bash Gate») | Перед правкой SKILL.md/CLAUDE.md: кто загружает, что меняется, нет ли дубля; перед разрушительной командой: что затронет + откат | `plugins/boost/README.md` (правила скиллов), `templates/CLAUDE.md` (1 строка) | пересказ, атрибуция ECC / zunoworks/gateguard | MIT ✔ |
| 6 | `skills/change-impact/SKILL.md@b38be6a` (п. 4) | Сверка scope ТР/SPEC с фактическим диффом: сделано сверх, не сделано, потребители не проверены | `odoo19-mvp-build:pr-review` | пересказ | MIT ✔ |
| — | `scripts/hooks/config-protection.js@b38be6a` | Хук-барьер для конфигов линтеров Odoo/Python | `plugins/boost/hooks/` — **только** после 2-го нарушения «Пола качества» в `observations/` | идея, код свой | MIT ✔ |

Не брать: файлы под CC BY-SA 4.0 (`osint-investigation`) и Apache-2.0
(логистика) — не нужны по теме.

## Риски и заметки

- Если всё же ставить ради одного скилла — нельзя: плагин неделим, а
  `hooks_enabled` по умолчанию `true`. Брать только тексты.
- Вставки 1–2 правят плагины маркетплейса `todoltd/claude-methodology-marketplace`
  — это делает сессия реализации по задаче `roadmap.md`.
- Вставки 3–5 проверять A/B по `evals/README.md` (с ними / без них).
