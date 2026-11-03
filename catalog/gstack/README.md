# gstack

- **Тип:** набор из 71 скилла + ~300 утилит (bun/TS/bash), свой браузер, хуки, телеметрия, память в `~/.gstack`
- **Источник:** https://github.com/garrytan/gstack
- **Версия / коммит:** `1.94.26.0`, `7caca3322e88f280111c495e68b1d917404ffdc5` (2026-11-03)
- **Лицензия:** MIT (© 2026 Garry Tan); сторонние части — Apache-2.0/MIT, перечислены в `NOTICE.md`
- **Дата разбора:** 2026-11-03
- **Вердикт:** **отклонить установку целиком; адаптировать 5 методов** (тексты своими словами в наши скиллы и правила)

## Что делает

«Виртуальная инженерная команда» Garry Tan (YC): слэш-команды по ролям —
CEO/eng/design-ревью плана, ревью PR, отладка, QA в настоящем браузере,
аудит безопасности, релиз (`/ship`), ретро, дизайн, iOS. Ставится
`./setup` в `~/.claude/skills/gstack`, работает на 12 агентах (Claude Code,
Codex, Cursor…). Скиллы генерируются из шаблонов, у каждого есть
контракт «Done means», общий преамбул (~22 КБ) и вызов рантайма
`gstack-skill-start`. 138.8k звёзд, релиз дважды в неделю.

## Какую слабость Claude закрывает

Непоследовательный процесс: чинить без корня, ослаблять тесты ради
зелёного CI, заявлять «проверено» без доказательства, раздувать скиллы.
Сильнейшая часть — не инструменты, а **дисциплина доказательств**,
вшитая в `review`/`ship`/`investigate`.

## Как устроен

Перечень компонентов, хуки, сеть и стоимость — в [`notes.md`](notes.md).
Главное:

- **Хуки:** `SessionStart` автообновление (team), `Stop` timeline (по
  умолчанию), AskUserQuestion-хуки для `/plan-tune` (с вопросом),
  team-`required` блокирует скиллы в репо без gstack. Плюс хуки во
  frontmatter отдельных скиллов (`careful`, `freeze`, `investigate`).
- **Сеть:** проверка обновлений раз в час (вкл.), телеметрия в Supabase
  (opt-in), **отправка кода/диффа в Codex для «второго мнения» по
  умолчанию ВКЛ**; каждая отправка пишет квитанцию в egress-журнал.
- **Контекст:** вызов `/review` ≈ 25–30k токенов текста до чтения кода;
  `investigate` ≈ 11k; без рантайма `bin/` — «degraded mode».
- **Облако:** память и learnings в `~/.gstack` теряются с контейнером;
  `cso` требует Docker и нативный лаунчер; браузер — Aside/Chromium-демон.

## Сводная таблица по компонентам

| Компонент | Что это | Есть у нас | Вердикт | Итог | Карточка |
|---|---|---|---|---|---|
| Gate Integrity (`review`/`ship`) | Ловля ослабления проверок в диффе: AC переписаны под код, код нюхает тест-окружение, пороги ослаблены, 0 тестов = зелёный | частично (`pr-review`: skip/noqa/мутации) | **адаптировать** → `odoo19-mvp-build:pr-review` | 16/18 | [items/gate-integrity.md](items/gate-integrity.md) |
| Claims Need Evidence + цитата перед находкой | Вид доказательства, stderr, «согласие агентов = одна точка»; находка без цитаты ≤ medium; для полей фреймворка цитировать порождающий код | частично (№28, `UNVERIFIED`) | **адаптировать** → `templates/CLAUDE.md`, `pr-review`, `repo-audit` | 16/18 | [items/claims-evidence.md](items/claims-evidence.md) |
| `write-skill` (из skill-diet) | Уровни размещения факта + лестница правки скилла + бюджет размера | частично (правила boost, `skill-feedback`) | **адаптировать** → правила `boost`, `weekly-review` | 16/18 | [items/write-skill.md](items/write-skill.md) |
| `test-audit` (планка ценности) | 4 вопроса перед тестом, карточка `protects/fails_when/why_new/no_claim`, каталог малоценных тестов | нет | **адаптировать** → `odoo19-mvp-build:testing`, `pr-review` | 16/18 | [items/test-audit.md](items/test-audit.md) |
| `investigate` + blast radius | «Без корня не чинить», стоп после 3 гипотез, DEBUG REPORT, лестница доказательств радиуса | нет | **адаптировать** → `boost:debug-root-cause` после A/B | 14/18 | [items/investigate.md](items/investigate.md) |
| `eval-plan` | Пререгистрация эвала, приманки для судьи, стоп-правила, плечо без стека | частично (`evals/README.md`) | идея → `plugins/boost/evals/README.md` | 14/18 | [items/eval-plan.md](items/eval-plan.md) |
| `careful`/`freeze`/`guard` | Хуки против разрушительных команд и правок вне каталога | права + auto mode | **отклонить**; приём «хуки во frontmatter скилла» записать | 12/18 | [items/careful-freeze-guard.md](items/careful-freeze-guard.md) |
| `cso` | Аудит безопасности v3 с воспроизведением в Docker | `security-review` (Strix) | **отклонить** рантайм; 3 строки идей | 11/18 | [items/cso.md](items/cso.md) |

Не отбирали (дубли или не наш профиль): `office-hours`, `plan-*-review`,
`autoplan`, `spec` (дублируют `interview-me`, `odoo-spec-writer`, `tr-*`;
ориентированы на стартап-продукт), `context-save`/`learn` (хуже
`cloud-memory` в облаке), `ship`/`land-and-deploy`/`canary` (GitHub/деплой
веб-продукта), `qa`/`browse`/`scrape` (свой браузерный демон), дизайн,
iOS, gbrain, `captain`, `ubicloud`.

## Проверка

A/B не делались (нужно разрешение пользователя; тексты gstack без
рантайма работают урезанно). Планы кейсов для каждой адаптации — в
карточках `items/`, раздел «Проверка».

| Задача | Без него | С ним |
|---|---|---|
| — | не прогонялось | не прогонялось |

## Оценка (набор целиком, как установка)

| Критерий | Балл (0–3) | Комментарий |
|---|---|---|
| Прирост | 2 | Сильные методы, но многие дублируют наши (`interview-me`, `cloud-memory`, Strix) |
| Частота | 2 | Ревью/отладка — еженедельно; остальное (дизайн, iOS, YC) не наш профиль |
| Надёжность | 2 | Контракты и тесты у них строгие, но завязаны на рантайм `bin/` и `~/.gstack` |
| Стоимость контекста | 0 | Преамбул ~5.5k токенов на каждый вызов, `/review` ≈ 25–30k; хуки SessionStart/Stop |
| Безопасность | 1 | 267 КБ `setup` и ~300 утилит не прочитать целиком; автообновление чужого кода в каждую сессию; код уходит в Codex по умолчанию |
| Поддержка | 3 | Очень активно, понятный автор |
| **Итого** | **10/18** | Ставить — нет; брать тексты методов |

## Что взять

Все строки — из коммита `7caca33`. Лицензия gstack MIT: допускается
перевод/адаптация с атрибуцией. Где gstack сам пересказывает чужое,
указываем и первоисточник.

| Идея | Исходный файл (`путь@SHA`) | Что берём | Куда у нас | Как | Лицензия |
|---|---|---|---|---|---|
| Ловля ослабления проверок: AC переписаны под код, код нюхает тест-окружение (`test_enable`), пороги/таймауты/assert ослаблены, 0 тестов = зелёный; три уровня и «один вопрос»; решение человека, без автофикса | `review/gate-integrity.md@7caca33`, `review/SKILL.md@7caca33` (шаги 4, 5c) | 4 паттерна (RH-10, RH-12, RH-15, PL-2) в Odoo-варианте + правило «находка gate = решение человека» | `odoo19-mvp-build:pr-review` → `references/review-discipline.md` (через `proposals/odoo19-mvp-build/pr-review`) | **только идея, своими словами**, без id RH-* и формулировок | MIT у gstack, но сам текст «adapted from …REWARD-HACKING-CATALOG», первоисточник не в `NOTICE.md` → осторожно, только идея |
| Вид доказательства, заглушённый stderr, «согласие агентов = одна точка», статусы DONE/DONE_WITH_CONCERNS/BLOCKED/NEEDS_CONTEXT | `investigate/sections/preamble.md@7caca33` (разделы «Claims Need Evidence», «Completion Status Protocol») | 3–4 правила | `templates/CLAUDE.md` | пересказ с атрибуцией | MIT, да |
| Цитата `file:line` перед находкой; без цитаты confidence ≤ medium; для символов фреймворка цитировать порождающий код | `review/SKILL.md@7caca33` («Pre-emit verification gate») | правило + Odoo-пример (`_inherit`, миксины, `related`) | `odoo19-mvp-build:pr-review`, `boost:repo-audit` | пересказ с атрибуцией | MIT, да |
| Уровни размещения факта и лестница правки скилла, бюджет размера, задачи-тесты до сокращения | `write-skill/SKILL.md@7caca33`, `write-skill/references/diet.md@7caca33`; первоисточник `nicobailon/skill-diet@5f41df1` | таблица уровней, 5 шагов, правило «рост >10% → сначала худеть» | `plugins/boost/README.md` (правила), `skill-feedback/references/weekly-review.md`, `plugins/boost/evals/README.md` | перевод/адаптация с атрибуцией обоих | MIT + MIT, да |
| Планка ценности теста и карточка `protects/fails_when/why_new/no_claim` | `test-audit/SKILL.md@7caca33` («Test value bar»), `docs/test-value-bar.md@7caca33` | 4 вопроса + карточка, Odoo-примеры `no_claim` (`sudo()`, `Form`, мок API) | `odoo19-mvp-build:testing`, проверка в `pr-review` | перевод/адаптация с атрибуцией | MIT, да |
| Отладка: без корня не чинить, стоп после 3 гипотез, правка >5 файлов → вопрос, skip/таймаут — не гипотеза, поиск без сырых данных, DEBUG REPORT | `investigate/SKILL.md@7caca33` | метод и формат отчёта | новый `boost:debug-root-cause` (≤150 строк), только после A/B | перевод/адаптация с атрибуцией | MIT, да |
| Blast radius: «один факт безопасности», искать где grep не видит, лестница доказательств из 5 ступеней, подтверждённые и снятые риски раздельно | `investigate/sections/blast-radius.md@7caca33`; первоисточник pstack `blast-radius` (© Lauren Tan) | лестница + формат | `boost:debug-root-cause/references/`, строка в `lean-change` | перевод/адаптация с атрибуцией обоих | MIT + MIT, да |
| Пререгистрация эвала, приманки для судьи, стоп-правила, пилот | `eval-plan/SKILL.md@7caca33` | 3 правила процесса | `plugins/boost/evals/README.md` | только идея, своими словами | MIT, да |
| Severity по худшему соседу, unknown ≠ unreachable, статус покрытия первой строкой | `cso/SKILL.md@7caca33` (Phase 12–13) | 3 строки | `odoo19-mvp-build:security-review/references/closure-and-severity.md` | пересказ | MIT, да |
| Хуки во frontmatter скилла живут только пока скилл вызван | `careful/SKILL.md@7caca33`, `investigate/SKILL.md@7caca33` (frontmatter `hooks:`) | приём | заметка для `roadmap.md` (барьеры без always-on) | только идея | MIT, да |

## Риски и заметки

- **Не ставить** в рабочие/клиентские репозитории: «outside reviews» по
  умолчанию отправляют код в Codex (OpenAI); team-режим добавляет в репо
  блокирующий хук и автообновление с GitHub в каждую сессию.
- Тексты gstack ссылаются на свои `bin/*` и пути `~/.claude/skills/gstack`;
  копировать их как есть бессмысленно — только метод.
- Первоисточники, которые стоит разобрать отдельно: `nicobailon/skill-diet`
  (MIT), pstack (Lauren Tan, MIT), неназванный «REWARD-HACKING-CATALOG».
- Приватный `todoltd/claude-methodology-marketplace` прочитать не удалось
  (`add_repo` отклонён) — сравнение `odoo19-*` по описаниям и по
  `proposals/`. Подробно в `notes.md`.
