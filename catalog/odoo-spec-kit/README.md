# odoo-spec-kit (focuz-ai)

- **Тип:** набор правил + скиллов + агентов + конфигурация линтеров (копируется в проект, не плагин)
- **Источник:** https://github.com/focuz-ai/odoo-spec-kit
- **Версия / коммит:** ветка `19.0` @ `23df08b4c1be58b632f8e77f163e5d2256925f9a`; `main` @ `e7d6e37`.
  Деревья `16.0`/`17.0`/`18.0`/`19.0`/`main` идентичны (`86c4484`) — по факту это кит под **Odoo 16.0**.
- **Лицензия:** MIT, «Copyright (c) 2026 Focuz AI» (сверено по `LICENSE`). Внутри есть чужое: `writing-skills`,
  `using-git-worktrees` (obra/superpowers, MIT), `writing-skills/anthropic-best-practices.md` (копия документации
  Anthropic — не MIT Focuz), три скилла `author: LIDR.co` (лицензия не установлена), `odoo-code-auditing`
  (адаптация `jeffrigby/somepulp-agents`, MIT).
- **Сверка:** `odoo/odoo@19.0` = `e0b25b7` (2026-11-03).
- **Дата разбора:** 2026-11-03
- **Вердикт:** **отклонить** как кит (5/18, надёжность 0); взять 4 идеи своими словами, см. «Что взять».

## Что делает

Испаноязычный кит «Spec-Driven Development» для Odoo поверх OpenSpec (Fission AI): `CLAUDE.md`/`AGENTS.md`/
`GEMINI.md`/`codex.md` — симлинки на `docs/base-standards.md`; 10 документов стандартов (backend, frontend, RPC,
топология моделей, git, тестовые шаги); 3 агента; 16 скиллов, из них цепочка `odoo-enrich-us` → `/propose` →
`odoo-build-and-qa` (apply → verify → `odoo-security-audit` → `odoo-adversarial-review` → авторемонт) → `odoo-ship`
(sync specs → archive → `odoo-commit` с push и PR); `pre-commit` по шаблону OCA (ruff, prettier, eslint, pylint-odoo,
OCA hooks).

## Какую слабость Claude закрывает

Заявлено: галлюцинации моделей/полей Odoo и «vibe-coding» без спецификации. На деле на 19.0 кит **усиливает** нашу
главную слабость (факты новой версии, `synthesis.md` п. 3): требует `attrs`/`states` и `<tree>`, советует
`type='json'`, `read_group`, XML-RPC, `hr.contract`, QUnit-хелперы и `useService("rpc")`. Модуль по этим правилам на
19.0 не установится (`attrs` → ValidationError, `ir_ui_view.py:495-497`).

## Как устроен

| Компонент | Оценка | Карточка |
|---|---|---|
| Стандарты `docs/*` + `CLAUDE.md` | 14 из 17 проверенных утверждений неверны для 19.0; противоречат друг другу (язык кода, язык коммитов, переводы) | [`items/standards.md`](items/standards.md) |
| Линтеры (`pre-commit`, pylint-odoo, ruff) | Шаблон OCA, настроен на 16.0; своих правил нет; версионные ловушки 19.0 не ловит | [`items/linters.md`](items/linters.md) |
| Скиллы workflow (`odoo-enrich-us`, `odoo-adversarial-review`, `odoo-security-audit`, `odoo-build-and-qa`, `odoo-ship`, `odoo-commit`) | Методически обычные, дублируют `odoo19-mvp-build`; 3 полезных правила | [`items/workflow-skills.md`](items/workflow-skills.md) |
| Утилиты (`odoo-code-auditing`, `odoo-scaffold`, `odoo-test-runner`, `odoo-explain`, `update-docs`, `show-spec-working`, `meta-prompt`, `sync-agent-symlinks`, `using-git-worktrees`, `writing-skills`) | Полезен только Odoo-чек-лист мёртвого кода; остальное есть у нас или чужое | в `items/workflow-skills.md` |

Права, сеть, установка: хуков Claude Code, MCP, телеметрии нет. Ставится `npm install -g @fission-ai/openspec@latest`
(без пина); `pre-commit` тянет 6 внешних репозиториев (пинованы). При копировании кита в проект хук
`oca-fix-manifest-website` перепишет `website` манифестов на `github.com/focuz-ai/odoo-spec-kit`
(`.pre-commit-config.yaml:34-35`), `odoo-scaffold` ставит `author: 'Focuz AI'`. Скиллы автономно коммитят, пушат
и открывают PR (`odoo-commit/SKILL.md:51-61`), цикл сборки — «без вмешательства человека».
`scripts/setup_assistant.py` — локальный stdlib-мастер путей, без сети. Ничего не запускали.

Активность: 124 коммита, 1 автор, две вспышки (2026-05-26…28 и 2026-11-02…03), ★2.

## Проверка

A/B не делали: кит на 19.0 заведомо вредит (правила противоречат исходникам), а полезные идеи — мелкие вставки в
наши тексты. Вместо A/B — построчная сверка с `odoo@19.0` (таблица в `notes.md`).

| Задача | Без него | С ним |
|---|---|---|
| Видимость кнопки по состоянию в форме 19.0 | не мерили; в наших прогонах база знает синтаксис 19.0 вью (`synthesis.md`, третий проход), ошибается в полях |  правило кита требует `attrs="{'invisible': …}"` → ValidationError при установке (`ir_ui_view.py:495-497`) |
| Список записей | `<list>` | `<tree>` (`backend-standards.md:190`) |
| JSON-маршрут для OWL | `type='jsonrpc'` | `type='json'` (deprecated alias, `http.py:812-818`) |
| Предварительный pre-commit на 19.0-модуле | — | `valid-odoo-versions=16.0` в обязательном гейте (вывод из конфигурации, не запускали) |

## Оценка

| Критерий | Балл (0–3) | Комментарий |
|---|---|---|
| Прирост | 1 | Сам кит на 19.0 вреден; ценны 4 небольших правила процесса и Odoo-чек-лист мёртвого кода |
| Частота | 1 | OpenSpec мы не используем; идеи пригодятся в сборке и аудите |
| Надёжность | 0 | Ветки версий фиктивны (одно дерево), 14/17 утверждений неверны для 19.0, внутренние противоречия |
| Стоимость контекста | 1 | `CLAUDE.md` 138 строк + 4 `alwaysApply`-документа ≈ 700 строк всегда; `writing-skills` ~2850 строк |
| Безопасность | 2 | Код прочитан; нет хуков/MCP/телеметрии; но авто-push/PR, `curl` к окружению, перезапись `website` манифестов, `openspec@latest` |
| Поддержка | 0 | 1 автор, ★2, версии не поддерживаются по-настоящему |
| **Итого** | **5/18** | Отклонить |

## Что взять

Лицензия Focuz — MIT; ниже только идеи и пересказ своими словами, код и тексты не копируем.

| # | Исходный файл (`путь@SHA`) | Что берём | Куда у нас | Как | Лицензия позволяет |
|---|---|---|---|---|---|
| 1 | `ai-specs/skills/odoo-code-auditing/references/dead-code-methodology.md@23df08b` (Odoo-переработка `jeffrigby/somepulp-agents@e56195b` `plugins/codebase-health/skills/code-auditing/references/dead-code-methodology.md`) | Чек-лист ложных «мёртвых» элементов Odoo: метод вызывается кнопкой `type="object"`, XML грузится манифестом без импорта, модель используется через `_inherit`/`env['…']` в другом аддоне, компонент в `registry`, хуки установки/миграции, только тесты/демо; классы «мёртв / подозрителен / ложное срабатывание», «подозрительное не удаляем» | `boost:repo-audit/references/` (и `lean-change` при удалении кода); после A/B на фикстуре | пересказ | да (MIT и MIT) |
| 2 | `docs/openspec-tasks-mandatory-steps.md@23df08b`:44-47, 108-113 | Пункт плана отмечается выполненным только после реально выполненной команды проверки; результат прогона пишется рядом с планом | T13: `boost:cloud-memory` (`memory/PLAN.md`), `build-orchestrator` (`BUILD_STATE.md`) | идея | да |
| 3 | `docs/base-standards.md@23df08b`:106-116 | Запрос изменения после начала кода: сначала ТР/SPEC (новые AC с ID), потом код, потом повторно `pr-review`/`security-review` | `odoo19-mvp-build:code-dev` / `build-orchestrator` (предложение владельцу маркетплейса, текст — в `proposals/odoo19-mvp-build/`) | идея | да |
| 4 | `ai-specs/skills/odoo-enrich-us/SKILL.md@23df08b`:39-43 | Ранний выход: перед проектированием `td.*` искать в Community/Enterprise/своих аддонах; если закрывается стандартом или настройкой — не проектировать, дать модуль и путь настройки | сверить с `tr-odoo-tech-design` (текст скилла недоступен); при отсутствии — вставка | идея | да |
| 5 | `ai-specs/skills/odoo-adversarial-review/SKILL.md@23df08b`:57-66 | У каждой находки поле «где чинить: код / тест / спецификация / документация» и класс «вопрос/допущение» | `odoo19-mvp-build:pr-review` (дополнение к 4-частной находке в `proposals/odoo19-mvp-build/pr-review/`) | идея | да |
| 6 | Негативный корпус: `docs/backend-standards.md@23df08b`:139-197, `docs/frontend-standards.md@23df08b`:165-169, 249-351, `docs/rpc-and-controllers.md@23df08b`:323-362, `docs/coding-guidelines.md@23df08b`:79 | Список кандидатов правил сверх плана T2, каждое сверено с `odoo@19.0` (см. `notes.md`): `read_group(`, `hr.contract`, `SavepointCase`, `div.oe_chatter`, JS `useService("rpc")`/`useService("user")`, `registry.category("fields").add(<Class>)`, `@web/../tests/helpers/`, `/xmlrpc`·`/jsonrpc` (warn) | T2 `boost:odoo19-lint` (правила и фикстуры пишем сами) | идея | да |
| 7 | — (побочная находка при сверке) `odoo/odoo@19.0` `odoo/upgrade_code/*.py` | Официальные кодмоды `odoo-bin upgrade_code` (`tree-to-list`, `sql-constraint`, `route-jsonrpc`): ссылаться на них в сообщениях T2 как на авто-исправление | T2 `boost:odoo19-lint` | идея; код не копировать | LGPL-3 — только идея |

Не брать: сам кит и OpenSpec-цепочку (дублирует `odoo19-mvp-build`), стандарты `docs/*` (неверны для 19.0),
конфиг `pre-commit` (настроен на 16.0, переписывает `website`), мультикопилотные симлинки, `writing-skills`
(чужие тексты, у нас `skill-creator`), формат спецификации `odoo-enrich-us` (слабее нашего: нет ID AC и трассировки).

## Риски и заметки

- Урок для `templates/CLAUDE.md` и T2: «одна переменная версии наверху» у них не дошла ни до линтеров, ни до примеров.
  Версию пишет человек, проверяет барьер (линтер сверяет префикс `version` манифеста с целевой версией).
- Если кто-то в команде принесёт этот кит в 19.0-проект: удалить `docs/backend-standards.md` §6, `frontend-standards.md`
  §4, §7, §8 и правила `attrs`/`states` в агенте — иначе модули не установятся.
- Не проверено: лицензия скиллов LIDR.co; фактический вывод pylint-odoo v9.3.15 на 19.0-модуле; тексты
  `odoo19-mvp-build` (приватный маркетплейс не подключён — `add_repo` отклонён классификатором прав).
