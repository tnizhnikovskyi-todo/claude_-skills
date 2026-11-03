# gstack — рабочий журнал

Сессия анализа, ветка `analysis/gstack`. Дата: 2026-11-03.

## Что смотрели

- Клон `https://github.com/garrytan/gstack` в scratchpad (вне репо), коммит
  `7caca3322e88f280111c495e68b1d917404ffdc5` (2026-11-03 16:39 UTC),
  `VERSION` = `1.94.26.0`. Лицензия MIT (© 2026 Garry Tan), сторонние
  части перечислены в `NOTICE.md` (Apache-2.0 и MIT, тексты в `licenses/`).
- Ничего не запускали: ни `./setup`, ни `bin/*`, ни хуки, ни браузерный
  демон. Только чтение файлов.
- Прочитаны целиком или по ключевым разделам: `README.md`,
  `docs/privacy.md`, `docs/install.md` (хуки), общий преамбул
  (`investigate/sections/preamble.md`), `investigate/SKILL.md`,
  `investigate/sections/blast-radius.md`, `review/SKILL.md` (шаги 1.5, 4, 5),
  `review/gate-integrity.md`, `cso/SKILL.md`, `cso/ACKNOWLEDGEMENTS.md`,
  `careful/SKILL.md`, `write-skill/SKILL.md` + `references/diet.md`,
  `test-audit/SKILL.md`, `eval-plan/SKILL.md` (шаги 1–1b),
  `office-hours/SKILL.md` (фаза 3), `NOTICE.md`.
- Активность: 908 коммитов с 2026-03-12, 491 за последний месяц, релизы
  дважды в неделю; ≈138.8k звёзд, 20.6k форков, 121 открытая issue
  (GitHub search API, 2026-11-03).

## Перечень компонентов

Это не плагин маркетплейса, а «фабрика»: 71 `SKILL.md` + ~300 утилит в
`bin/` (bun/TS/bash), свой браузер, генератор скиллов из шаблонов
(`SKILL.md.tmpl` → `SKILL.md`), контракты «Done means», телеметрия,
собственная память (`~/.gstack/`), опциональный gbrain (PGLite/Supabase).

| Группа | Скиллы |
|---|---|
| Планирование | `office-hours`, `plan-ceo-review`, `plan-eng-review`, `plan-design-review`, `plan-devex-review`, `autoplan`, `spec`, `plan-tune` |
| Код и ревью | `review`, `investigate`, `verify`, `ship`, `land-and-deploy`, `modernize`, `deslop-shared-libs`, `test-audit`, `health`, `codex` (второе мнение), `cso` (безопасность), `captain` (оркестрация агентов) |
| QA и браузер | `qa`, `qa-only`, `browse`, `scrape`, `skillify`, `setup-browser-cookies`, `open-gstack-browser`, `pair-agent`, `benchmark`, `canary`, `devex-review` |
| Дизайн | `design-consultation`, `design-shotgun`, `design-html`, `design-review`, `design-motion`, `diagram`, `make-pdf` |
| iOS | `ios-qa`, `ios-fix`, `ios-design-review`, `ios-clean`, `ios-sync` |
| Документация | `document-generate`, `document-release`, `retro`, `landing-report` |
| Память/контекст | `context-save`, `context-restore`, `learn`, `setup-gbrain`, `sync-gbrain` |
| Безопасность сессии | `careful`, `freeze`, `unfreeze`, `guard` (хуки в frontmatter скилла) |
| Мета | `write-skill`, `eval-plan`, `benchmark-models`, `gstack-upgrade`, `ubicloud`, корневой `SKILL.md`-роутер |

Агентов (`agents/`) как субагентов Claude Code нет; MCP-серверов в составе
нет (gbrain регистрирует MCP только через `setup-gbrain`).

## Что ставится на машину и права

- `./setup` (267 КБ bash): ставит/проверяет Bun ≥ 1.3.3 (может скачать
  `bun.sh/install`), собирает бинарники, качает Chromium через Playwright,
  копирует в `~/.claude/skills/gstack`, пишет хуки в
  `~/.claude/settings.json`.
- Хуки: `SessionStart` автообновление (в team-режиме), `Stop` «timeline»
  (по умолчанию включён), `PreToolUse`/`PostToolUse` на AskUserQuestion для
  `/plan-tune` (спрашивает перед установкой). Team-режим `required`
  добавляет в репозиторий хук, блокирующий скиллы без gstack.
- Скиллы `careful`/`freeze`/`investigate` объявляют хуки во frontmatter:
  они активны только пока скилл вызван (интересный приём).
- Состояние: `~/.gstack/` (сессии, timeline, learnings, analytics,
  egress-журнал). В облачном контейнере это теряется.

## Сеть и телеметрия

- Телеметрия: opt-in, спрашивает один раз; уходит в Supabase (имя скилла,
  длительность, ОС, версия, класс ошибки; не код и не пути).
- Проверка обновлений: по умолчанию ВКЛ, `git ls-remote` + GET `VERSION` с
  GitHub раз в час.
- «Outside reviews»: по умолчанию ВКЛ — `/review`, `/ship`, планы и др.
  отправляют код/дифф в Codex (OpenAI) под логином пользователя. Для
  клиентского кода это утечка без явного решения; отключается
  `gstack-config set codex_reviews disabled`.
- Плюс: каждая отправка пишет квитанцию в хэш-цепочку
  `~/.gstack/security/egress.jsonl`.
- Автообновление с `main`/`stable` = чужой код подтягивается в каждую
  сессию без ревью (риск цепочки поставок).

## Стоимость контекста

- Каждый скилл грузит общий преамбул ~22 КБ (≈5.5k токенов) плюс свой текст:
  `investigate` 21 КБ, `review` 60 КБ + `checklist.md` 25 КБ + секции,
  `ship` 61 КБ. Один вызов `/review` ≈ 25–30k токенов до чтения кода.
- Преамбул на каждом вызове гоняет `gstack-skill-start` (bash), логирует
  вопросы, предлагает «tune», телеметрию. Без установленного `bin/` скиллы
  работают в «degraded mode» — то есть тексты без рантайма неполноценны.

## Сравнение с нашим (кратко, подробно в items/)

- `review` vs встроенный `code-review` и наш `odoo19-mvp-build:pr-review`
  (`proposals/odoo19-mvp-build/pr-review`): у нас уже есть грep на
  `skip`/`noqa`/`except: pass`, мутационная проверка, Prove-It. Сверх
  нашего у gstack: RH-10 (правка AC как «прогресс»), RH-12 (код,
  нюхающий тестовое окружение), RH-15 (ослабление порогов/таймаутов,
  `assertEqual`→`assertTrue`), PL-2 (ноль тестов = зелёный), «цитируй
  строку, иначе confidence ≤5» с оговоркой про символы, порождённые
  фреймворком (у Odoo: `_inherit`, `related`, поля из миксинов).
- `investigate` vs ничего специального у нас (встроенного «debug»-скилла
  нет; `lean-change` про объём правки). Новое: железный закон «без
  корня не чинить», стоп после 3 неудачных гипотез, отчёт DEBUG REPORT,
  «лестница доказательств» blast radius (из pstack, MIT).
- `cso` vs `security-review` (встроенный и наш Odoo-вариант со Strix):
  рантайм `cso` требует нативного лаунчера и Docker — в облаке не
  работает. Идеи («supported finding» из 4 условий, «неизвестная
  достижимость ≠ недостижимо», severity по худшему соседу) почти
  совпадают с тем, что мы уже взяли из Strix; добавочно немного.
- `context-save`/`learn` vs `boost:cloud-memory`: у нас память в git и
  переживает контейнер, у них в `~/.gstack` — наш вариант лучше для облака.
- `office-hours`/`spec` vs `boost:interview-me`, `odoo-spec-writer`,
  `tr-*`, продажные `brief-prep-pack`/`client-questions-pack`: дублируют,
  ориентированы на стартап-продукт, а не на внедрение Odoo.
- `write-skill` vs `anthropic-skills:skill-creator`, наш `skill-feedback`
  и правила `plugins/boost/README.md`: компактные «уровни» и «лестница
  правки» (из skill-diet, MIT) — хорошее дополнение к нашим правилам.
- `eval-plan` vs `plugins/boost/evals/README.md`: у нас практика
  `claude plugin eval`; у них пререгистрация, приманки (decoys), стоп-
  правила и обязательное плечо «без стека». Полезно как процесс.
- `careful`/`freeze`/`guard`: в Claude Code уже есть права и
  классификатор auto mode; полезна только идея «хуки в frontmatter
  скилла, живут пока скилл активен».
- `browse`/`qa`: нужен Aside или свой Chromium-демон; в облаке есть
  Playwright и встроенный `run`. Не проверяли, не берём.

## Доступ к репозиториям для сравнения

- `todoltd/claude-methodology-marketplace` (приватный): `add_repo` на
  чтение отклонён классификатором auto mode. Сравнивал `odoo19-*` по
  описаниям скиллов в сессии и по нашим `proposals/odoo19-mvp-build/`.
  Из приватного репо ничего не читали и не копировали.
- `tnizhnikovskyi-todo/sale_todo_claude` (публичный): через GitHub MCP
  доступ закрыт (не в скоупе), склонирован `git clone --depth 1` в
  scratchpad для чтения списка скиллов `plugins/*/skills/*`.

## Проверки (A/B)

Не делались: по правилам нужен явный запуск и разрешение; к тому же
тексты gstack без рантайма работают в degraded mode. План A/B для
адаптаций — в карточках `items/` (раздел «Проверка»).

## Открытые вопросы

1. `review/gate-integrity.md` говорит «Adapted from the
   just-say-no-to-process-porn-and-ceremony skill's REWARD-HACKING-CATALOG»,
   но этого источника нет в `NOTICE.md`. Лицензия первоисточника
   неизвестна → берём только идеи своими словами, без копирования
   формулировок и id. Стоит найти первоисточник (отдельная задача хаба).
2. `write-skill` и `investigate/sections/blast-radius.md` — пересказы
   `nicobailon/skill-diet@5f41df1` (MIT) и pstack (Lauren Tan, MIT).
   Кандидаты на отдельный разбор первоисточников.
3. Нужно ли разрешение на A/B адаптаций (`gate-integrity` в `pr-review`,
   `debug-root-cause` в `boost`)? Решает пользователь.
