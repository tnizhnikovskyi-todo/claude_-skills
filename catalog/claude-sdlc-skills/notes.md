# claude-sdlc-skills — рабочий журнал

## 2026-11-03 — разбор

### Получение и происхождение

- Источник: https://github.com/TsCarpe/claude-sdlc-skills, ветка `main`.
- Разобранный коммит: `49ef0b3629efa5a1e227d8b2f998a04506c6c1e4`
  (2026-10-28 20:24 +0800). Клон `--depth 50` в scratchpad, вне нашего репо.
  Первый полный клон через прокси завис, перезапущен неглубоким.
- Лицензия: файл `LICENSE` — MIT, «Copyright (c) 2026 TsCarpe». Совпадает с
  поиском. Других лицензий и чужих файлов с иной лицензией не нашёл; весь
  код и тексты одного автора (все коммиты `TsCarpe`). В `README.md` «致谢» и
  `docs/workflow.md` §6 автор сам называет источники идей:
  addyosmani/agent-skills (MIT), Claude best practices, AI-Native SDLC
  Playbook (academy.claude.com), статья Anthropic про code review. Прямых
  копий чужого текста не видно, кроме враждебного промпта (см. ниже).
- Активность: 52 коммита в окне `--depth 50` с 2026-09-16 по 2026-10-28,
  один автор, CI (`.github/workflows/validate.yml`), CHANGELOG 64 КБ.
  ★65 по поиску (API GitHub в сессии закрыт, звёзды не перепроверены).
- Язык: всё по-китайски (описания скиллов двуязычные). Стек автора:
  Java DDD + MySQL + веб-фронт, Feishu (`lark-cli`), свой веб-«платформа».

### Состав (9 скиллов, 185 файлов)

| Скилл | SKILL.md | Что |
|---|---|---|
| `sdlc-intent` | 108 + 9 references (~900) + 4 скрипта | Приём PRD: digest из 8 блоков, затем аудит по 7 слоям + PM-чек-лист |
| `sdlc-design` | 82 | design.md из digest: альтернативы, контракты, таблица решений C/H |
| `sdlc-test` | 140 + много references | cases (7 техник) / dev / static / exec (браузер) / spec (Playwright) / report |
| `sdlc-gate` | 218 + 4 references + 2 скрипта | Враждебный гейт по design + cases: A=4 / B=2 субагента / C=самопроверка, человек выносит решения |
| `sdlc-doubt` | 126 | Враждебная перепроверка решения субагентом (как doubt-driven у addyosmani) |
| `sdlc-ui-visual` | 95 | Figma → скриншоты → пиксельный diff |
| `sdlc-release-check` | 149 | Java/SQL diff → ключи Apollo/Nacos, xxl-job, DDL |
| `sdlc-guardrails` | 60 + engine | `PostToolUse` на Write/Edit → `check.py` по `guardrails.yaml` |
| `sdlc-sync` | 180 | curl к своей платформе автора (`SDLC_PLATFORM_URL`, по умолчанию 127.0.0.1:8080) |

### Безопасность (только чтение, ничего не запускал)

- Сеть в коде: `verify_dev.py` — `urllib` к health/smoke URL из конфига
  проекта (localhost); `sdlc-sync` велит Claude делать `curl` к своей
  платформе (её кода в репо нет); `parse_doc.py` вызывает `lark-cli` для
  скачивания медиа Feishu. Телеметрии нет, внешних хостов в коде нет.
- `verify_dev.py` выполняет команды сборки/запуска из `sdlc/env/*.md`
  через `shell=True` — доверие к конфигу проекта, как к Makefile.
- Хук: только шаблон `sdlc-guardrails/templates/settings-hook.json`
  (`PostToolUse` Write|Edit, `python3 ~/.claude/skills/.../check.py`,
  timeout 20). Ставится вручную, сам не регистрируется. Плагин хуков не
  объявляет (`marketplace.json` — только skills).
- `check_trace.py`, `guard_dev.py`, `check.py` — stdlib (`re`, `sys`,
  `pathlib`, `json`), только чтение файлов `sdlc/`.
- Ставится: `npx skills add TsCarpe/claude-sdlc-skills` (skills.sh) или
  маркетплейс; для `sdlc-test spec` — `npm install @playwright/test@1.61.0`
  в `sdlc/`, CI ставит Pillow 12.3.0. MCP: `codegraph`, `mysql`,
  `chrome-devtools` — внешние, у автора свои.
- `sdlc-gate` описание триггерится на «开始开发/直接开发/写代码/实现功能»
  (начать разработку, написать код) — перехватывает обычную разработку;
  без папки `sdlc/` сам себя отключает (Step 0).

### Сравнение с нашим

- Доступ к `todoltd/claude-methodology-marketplace`: `add_repo` отклонён
  классификатором авто-режима. Тексты `tr-review` (109 строк),
  `odoo-spec-writer` (123), `tr-usecases-acceptance`, `tr-odoo-tech-design`
  нашлись в `~/.claude/skills/synced/*/` (как у сессии nacl). Тексты
  `odoo19-mvp-build:pr-review`, `track-convergence`, `testing` не доступны —
  сравнение по `proposals/odoo19-mvp-build/` и описаниям. Ничего из
  приватных текстов не копировал, только пересказ.
- `tr-review`: один проход чек-листа той же сессией, проверка «вимога → AC →
  реалізація → оцінка», Odoo 19, плейсхолдеры, Формат C. Нет: проверки
  пропусков через справочные таблицы (данные «введено/не используется»,
  «используется/нигде не вводится», «нет источника», симметрия параллельных
  структур, висячие ссылки), «данные в работе при смене состояния/настройки»,
  «настройка × состояние», правила «конфликт не выбирать сторону»
  (это у нас уже предложено из requirement-engineer).
- `sdlc-gate` против `independent-check` (отклонён, Δ=0): там свежий
  критик смотрит ОДИН артефакт на заложенные ошибки — модель и так их
  находит. Здесь главный механизм иной: два артефакта (design и cases)
  выводятся из одного требования **независимо** (cases запрещено читать
  design), и только 4-й агент сравнивает их; расхождение = сигнал о
  неоднозначности требования, которую ни один артефакт по отдельности не
  показывает (оба внутренне согласованы). Роли 1–3 (архитектура, данные,
  тестируемость) — это и есть independent-check, их брать незачем.
  Наш ТР пишется одной цепочкой (`tr-usecases-acceptance` → `tr-odoo-tech-design`
  читает AC), независимости нет, поэтому сравнивать нечего — механизм
  у нас отсутствует. Прирост не измерен ни у автора (числа удалены из README),
  ни у нас.
- `sdlc-doubt`: шаги CLAIM/EXTRACT/DOUBT/RECONCILE/STOP и 4 класса —
  пересказ `doubt-driven-development` из addyosmani/agent-skills (мы его
  уже разобрали и отклонили в виде `independent-check`). Новое только
  «2+ раунда с находками, но 0 принято — театр, остановись».
- `pr-review` (по `proposals/`): 4-частная находка, «пол», мутации, Prove-It.
  У gate сверх: маховик ложных срабатываний (отклонённые с причиной →
  в промпт следующего ревью), правила повторного раунда (наследование
  решений, только изменённое, предохранитель на 3-м раунде), «ack ≠ допуск».

### A/B

Не делал: внешний код не запускал, адаптированных текстов ещё нет.
План проверки — в `README.md` «Проверка».

### Открытые вопросы

1. Разрешить `add_repo` на чтение маркетплейса, чтобы сверить с
   `pr-review`/`track-convergence`/`testing`.
2. Делать ли A/B «слепого вывода AC» (items/sdlc-gate.md) — это главный
   кандидат, и он ровно на границе нашего отказа от independent-check.
