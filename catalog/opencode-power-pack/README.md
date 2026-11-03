# OpenCode Power Pack

- **Тип:** плагин (сборник 55 скиллов) для Claude Code, Codex, OpenCode 1/2, Pi
- **Источник:** https://github.com/waybarrios/opencode-power-pack (★549)
- **Версия / коммит:** v0.6.0, `c3328ad1633c1561026532f29b718a2380bc52ee` (2026-10-27)
- **Лицензия:** заявлена «MIT AND Apache-2.0»; по скиллам см. ниже, у скиллов безопасности фактически **CC BY-SA 4.0** (Trail of Bits)
- **Дата разбора:** 2026-11-03
- **Вердикт:** **отклонить как плагин; адаптировать 5 небольших вставок** (по 1–3 строки) в `security-review`, `pr-review`, `criteria.md`

## Что делает

Собирает в один плагин чужие скиллы (Hugging Face, Anthropic, piolium /
Trail of Bits, мелкие авторы) и делает их переносимыми между четырьмя
агентами. Свой скилл один: `humanizer`. Сверху: профили наборов, eval-
инфраструктура и необязательный sandbox-CLI.

## Какую слабость Claude закрывает

Как сборник — никакую новую: всё лучшее доступно в первоисточниках. Внутри
полезны методы безопасности Trail of Bits: закрывать находку с
доказательством, искать fail-open, оценивать риск зависимостей и CI-агентов.

## Как устроен

- Для Claude Code: `.claude-plugin/plugin.json` с одним полем
  `"skills": "./skills/"`. Нет хуков, MCP, `settings.json`.
- `UPSTREAMS.json`: у каждого скилла есть репозиторий, коммит, путь и blob
  источника. Это образцовая прозрачность, но лицензия посредника (piolium)
  записана вместо первоисточника.
- `skillsets.json`: профили `recommended`, `review`, `security`,
  `huggingface`… работают только через их npm-установщик.
- `bin/` sandbox-CLI на `@anthropic-ai/sandbox-runtime@0.0.73`, ставится
  отдельно через npm и вызывается явно.
- `evals/behavioral/`: 12 кейсов против prompt-injection и раскрытия
  секретов, плюс «мутации» ответов, которые грейдеры обязаны поймать.

## Перечень скиллов

| Группа | Скиллы | Источник | Для нас |
|---|---|---|---|
| Ревью кода | `code-review`, `code-reviewer`, `code-quality`, `design-patterns` | Anthropic official (Apache-2.0); Firstpick (MIT) | Дубль встроенного `code-review`, `boost:repo-audit` |
| Фичи | `feature-dev`, `code-architect`, `code-explorer` | Anthropic official | Дубль официального плагина `feature-dev` |
| Безопасность (14) | `security-review` | Anthropic `claude-code-security-review` (MIT) | Дубль встроенного |
| | `fp-check`, `differential-review`, `insecure-defaults`, `sharp-edges`, `variant-analysis`, `supply-chain-risk-auditor`, `agentic-actions-auditor`, `semgrep`, `semgrep-rule-creator`, `semgrep-rule-variant-creator`, `codeql`, `sarif-parsing` | Trail of Bits через piolium (CC BY-SA 4.0, помечены MIT) | Идеи — см. «Что взять» |
| | `security-threat-model`, `vuln-report` | piolium | Редко нужно |
| Правила проекта | `agents-md-improver`, `agents-md-revise` | Anthropic official | Пересекается с `init`, `boost:skill-feedback`, `cloud-memory` |
| Авторинг | `skill-creator`, `mcp-builder` | `anthropics/skills` | Уже есть `anthropic-skills:skill-creator` |
| Фронт и текст | `frontend-design`, `ai-slop`, `humanizer`, `paper-summarizer` | Anthropic; omp-designer; свой; Firstpick | `humanizer` (испанский/английский) ≈ наш шаг Humizer в протоколах |
| ML / Hugging Face / AWS (25) | `hf-*`, `huggingface-*`, `trl-training`, `transformers-js`, `train-sentence-transformers` | `huggingface/skills` (Apache-2.0) | Не наш профиль |

Карточки: [`items/`](items/) — 6 штук (отобраны все, что касаются ревью и аудита).

| Скилл | Вердикт | Итог | Главное |
|---|---|---|---|
| [`insecure-defaults`](items/insecure-defaults.md) | адаптировать 2 строки | 13 | fail-open конфигурации: `get_param(default=…)`, TLS по умолчанию |
| [`supply-chain-risk-auditor`](items/supply-chain-risk-auditor.md) | адаптировать в `criteria.md` | 13 | 6 признаков риска вместо одной шкалы «Поддержка» |
| [`differential-review`](items/differential-review.md) | адаптировать 2 идеи | 11 | риск файла по содержанию; переопределения через `_inherit` (сравнение с базой у нас уже есть) |
| [`fp-check`](items/fp-check.md) | адаптировать 2 идеи | 10 | шаг 0 «перескажи находку», цепочки из `ruled_out` (достижимость у нас уже есть) |
| [`agentic-actions-auditor`](items/agentic-actions-auditor.md) | отложить | 11–12 | 9 векторов атаки на CI с ИИ-агентом; нужно, если есть такие workflow |
| [`code-review`](items/code-review.md) | отклонить, 2 идеи | 10 | «упавший критик ≠ нет находок» — прямо ложится на раунд критиков `pr-review`; пин коммитов PR |

## Сравнение с нашими

Сверено с действующими текстами `odoo19-mvp-build` (`todoltd/claude-methodology-marketplace@7acde05`, приватный, только чтение; текст не копируем). Наши предложения Strix/ponytail там уже влиты.

| Наш скилл | Что у них сверх | Что дублирует |
|---|---|---|
| `security-review` (орг., действующий) | Явный **fail-open конфигурации модуля**: `get_param(key, default='<секрет/URL>')`, `verify=False` по умолчанию (`insecure-defaults`); шаг 0 «перескажи находку» и цепочки из `ruled_out` (`fp-check`) | Закрытие кандидата тремя состояниями, «аргументируй другую сторону», VULN только при показанной достижимости, «понижай, не удаляй», скоуп диффа с изменённым default, «контроль, который открывается при ошибке», «что поставляется, то и считается» |
| `pr-review` (орг., действующий) | Риск файла по содержанию, а не размеру; переопределения изменённого метода через `_inherit`; «критик-субагент упал/ответил частично → это «Not checked», а не «чисто»»; пин `merge-base` | 4-частная находка, регрессия / newly reached / pre-existing через `git show`/`git blame`, пол качества, мутационная проверка, Prove-It, «Not checked» |
| `boost:repo-audit` | Odoo-таблица fail-open в `odoo-checklist.md`; признаки риска зависимостей | Ранжирование, формат, «нет случая — нет находки», «не проверено» |
| `boost:lean-change` | — (у них нет аналога; `code-review` только флагует scope creep) | — |
| `boost:automation-audit` | Векторы атаки на CI (`agentic-actions-auditor`) | — |
| `plugins/boost/evals` | — | Мутации грейдеров = наш «негативный контроль» (`evals/README.md`) |

## Проверка

A/B не делали. Внешний код не запускали.

| Задача | Без него | С ним |
|---|---|---|
| — | — | — |

Кандидат на A/B: две строки fail-open в Dimension 6 `security-review` и правило «упавший критик → Not checked» в `pr-review`; фикстуры
`proposals/odoo19-mvp-build/tests/fixtures/` плюс одна новая с
`get_param(..., default='секрет')`.

## Оценка (плагин целиком)

| Критерий | Балл (0–3) | Комментарий |
|---|---|---|
| Прирост | 1 | Ценное — в первоисточниках; ревью дублирует встроенное |
| Частота | 1 | Из 55 нам регулярно нужны 3–4 |
| Надёжность | 2 | Тексты чистые, триггеры узкие; конфликт с встроенными `code-review`/`security-review` |
| Стоимость контекста | 0 | 55 описаний ≈ 14 тыс. символов ≈ 3.6 тыс. токенов в каждой сессии |
| Безопасность | 2 | Для Claude Code только тексты, без хуков и MCP. Минус: неверная лицензия у 12 скиллов |
| Поддержка | 2 | Активен (117 коммитов за 6 месяцев), один автор; копии отстают от первоисточников |
| **Итого** | **8** | |

## Что взять

| # | Идея | Исходный файл | Куда у нас | Как | Лицензия |
|---|---|---|---|---|---|
| 1 | **fail-open конфигурации:** «что будет, если параметра нет?» — `get_param(key, default='<секрет/URL>')` = находка уровня хардкода; `verify=False` / `verify_ssl` по умолчанию `False`. Остальное (`auth='public'`, `groups=`, `except: pass` в проверке) у нас уже есть | `skills/insecure-defaults/SKILL.md@c3328ad` (ToB `plugins/insecure-defaults@711af09`) | `security-review` Dimension 6 (2 строки); строка в `boost:repo-audit/references/odoo-checklist.md` | Своими словами, ссылка на Trail of Bits | CC BY-SA 4.0 → только идея |
| 2 | **Шаг 0** «перескажи находку: что / корень / триггер / влияние / кто атакует» + поиск **цепочек** из `ruled_out`/понижённых в конце. Достижимость и «другую сторону» у нас уже есть | `skills/fp-check/SKILL.md@c3328ad` (ToB `plugins/fp-check@711af09`) | `security-review`, «Closing every candidate» | Своими словами | CC BY-SA 4.0 → только идея |
| 3 | **Риск файла по содержанию** (в Odoo HIGH = `security/`, `ir.rule`, контроллеры, `sudo()`, `account.*`; «рефакторинг» с удалённой проверкой = HIGH) + переопределения изменённого метода через `_inherit` в других аддонах. `git blame` для регрессий у нас уже есть | `skills/differential-review/SKILL.md@c3328ad` (ToB `plugins/differential-review@711af09`) | `pr-review`, «Review discipline»; `security-review/references/diff-scope.md` | Своими словами, Odoo-вариант | CC BY-SA 4.0 → только идея |
| 4 | **6 признаков риска** (один мейнтейнер, заброшен, непопулярен, рискованные возможности, CVE, нет `SECURITY.md`) + «цифры только из `gh`» + наш признак «цепочка лицензий» | `skills/supply-chain-risk-auditor/SKILL.md@c3328ad` (ToB `plugins/supply-chain-risk-auditor@711af09`) | `criteria.md`, подсказки к «Поддержке» и «Безопасности» (правит главная сессия) | Своими словами | CC BY-SA 4.0 → только идея |
| 5 | «Критик или субагент упал / вернул пусто / частично ≠ нет находок» → участок в «Not checked» (сейчас при недоступности только «single pass»); ревьюить `merge-base(base, head)..head` | `skills/code-review/SKILL.md@c3328ad` (Anthropic `claude-plugins-official@bdca23e`) | `pr-review`, раунд критиков и Inputs | Пересказ | Apache-2.0, атрибуция |
| 6 | (отложено) 9 векторов атаки на CI с ИИ-агентом | `skills/agentic-actions-auditor/references/vector-*.md@c3328ad` | `boost:automation-audit`, если у нас есть `claude-code-action` | Только идея | CC BY-SA 4.0 |

Если понадобится текст скиллов безопасности целиком — брать из
`trailofbits/skills`, а не из power-pack или piolium: там свежее и лицензия
верная.

## Риски и заметки

- **Лицензия.** 12 скиллов piolium происходят из
  `trailofbits/skills`, 5 почти дословно (`sharp-edges` отличается на 8 строк из
  289, `fp-check` на 18 из 112), а у ToB CC BY-SA 4.0. Пометка MIT, скорее
  всего, неверна. Подробности в `notes.md`.
- **Цена.** Ставить целиком нельзя: 3.6 тыс. токенов на описания в каждой
  сессии и пересечение с встроенными скиллами.
- **Переносимость** на Claude Code хорошая (готовый маркетплейс), но
  выборочно поставить часть скиллов через `/plugin install` нельзя.
- Сам подход автора полезен как образец: `UPSTREAMS.json` с коммитом и
  blob каждого источника — так же стоит вести `references/attribution.md`
  в `boost`.
