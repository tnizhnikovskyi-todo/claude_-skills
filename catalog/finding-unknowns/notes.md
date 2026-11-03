# finding-unknowns — рабочий журнал

Сессия анализа, 2026-11-03. Ветка `analysis/finding-unknowns`.

## Что разбираем

- Репозиторий: https://github.com/Neeeophytee/finding-unknowns-skills
- Разобранный коммит: `ca5696a0f08d2de6b2997fff1d6cc05c3ed587cc` (2026-09-28), версия плагина 1.5.0.
- Клон: scratchpad сессии, вне нашего репозитория. Ничего не запускали:
  ни `scripts/*.py`, ни `evals/*.py`, ни тесты, ни `npx skills add`.

## Лицензия и происхождение (проверено по файлам)

- `LICENSE` — стандартный текст MIT, `Copyright (c) 2026 Neeeophytee`.
  Поиск показал MIT — совпадает.
- История `LICENSE`: в первом коммите `af70365` в текст MIT была вставлена
  фраза-атрибуция Thariq Shihipar; в `22ca894` («Restore standard MIT license
  and preserve source attribution», 2026-09-09) её перенесли в `NOTICE.md`,
  сам `LICENSE` стал чистым MIT. Подвоха (NC, SA, «All rights reserved») нет.
- `NOTICE.md`: 11 исходных скиллов и `guidance/` — «дистилляция» техник из
  двух публичных эссе Thariq Shihipar (Anthropic, команда Claude Code):
  *A Field Guide to Fable: Finding Your Unknowns* и *The new rules of context
  engineering for Claude 5 generation models*. Текст инструкций — авторский
  (по словам автора, «original instruction text»), эссе сохраняют свои условия.
  `assumption-test`, `test-blindspots` — собственные расширения автора;
  `regression-proof` — по посту *Spending your effort* (claude.dev).
- Вывод для нас: текст скиллов можно брать под MIT с атрибуцией
  Neeeophytee; сами эссе не копируем (их лицензия не проверялась), идеи из
  эссе — только пересказом своими словами со ссылкой.
- Автор в `references.bib`: Shilpa Mitra (аккаунт Neeeophytee).

## Состав (прочитаны все 14 `SKILL.md` целиком, 23–29 строк каждый)

blindspot-pass, brainstorm-prototypes, interview-me, reference-hunt,
implementation-plan, implementation-notes, pitch-packager, change-quiz
(эссе 1); context-audit, agent-interface-design, progressive-disclosure
(эссе 2); assumption-test, test-blindspots (расширения автора);
regression-proof (пост). Плюс `guidance/finding-unknowns.md` — тот же метод
одним файлом для `CLAUDE.md`/`AGENTS.md`.

Объём: описания всех 14 ≈ 3,7 КБ (~1 000 токенов всегда в контексте после
установки), тела 1,8–3,2 КБ (~500–800 токенов на вызов), всего 32 КБ.

## Безопасность

- Только markdown. Хуков, MCP-серверов, `bin/`, команд, агентов нет.
- `.claude-plugin/plugin.json` перечисляет только 14 папок `skills/`.
  `source: "./"` — при установке копируется весь репозиторий, включая
  `scripts/` и `evals/`, но они ничего не регистрируют и сами не запускаются.
- `scripts/validate.py` — проверка фронтматтера (yaml, pathlib, без сети);
  `scripts/build_site.py` — генерация статического сайта oss.flowstacks.xyz
  (только строки URL, сетевых вызовов нет). `evals/fixtures/*.py` — данные в
  памяти. CI: `permissions: contents: read`.
- Телеметрии нет. Сетевых вызовов в коде нет.
- Внешний установщик `npx skills add` (Vercel) — чужой инструмент, нам не нужен.
- Скиллы `assumption-test`, `test-blindspots`, `regression-proof` предлагают
  агенту запускать эксперименты/тесты, но с явными ограждениями: без продовых
  записей, платежей и необратимых действий без разрешения.
- Оценка безопасности: **3**.

## Активность

16 коммитов, 2026-07-05 … 2026-09-28, один автор, ★361 (по поиску). Релизы
1.1–1.5. Последние коммиты — в основном сайт/бейджи. Поддержка: **2**.

## Честность автора о доказательствах

`evals/README.md` прямо пишет: CI проверяет только упаковку; сравнений
«с/без» агента не проводилось, «publication does not establish behavioral
improvement». Протокол оценки хороший (свежая среда, тот же агент с/без,
не давать ключ, негативные кейсы, held-out вариант) — совпадает с нашим.

## Сравнение с нашим: что смотрели

- `plugins/boost/skills/interview-me/SKILL.md` (наш, из addyosmani/agent-skills).
- `proposals/odoo19-discovery/` (вставки A–D для `session-question-builder`
  и `kickoff-question-builder`).
- Публичный `tnizhnikovskyi-todo/sale_todo_claude` @ `2a7f7c1`: читали
  `data-completeness-scorer` (Q-N, теги [КО]/[ВО]/[ПП], `G-N` гипотезы,
  «одне невідоме тримає ×2/×3»), `client-questions-pack` (раздел «Хоче
  інакше», «невідомо, потрібен аналітик»). Лицензия этого репо — внутренняя
  ToDo; ничего не копировали, только сверяли.
- Карточки `catalog/ba-skills/`, `catalog/requirement-engineer/`,
  `catalog/kevinlin-skills/`, `catalog/nacl/`, `catalog/agent-skills/`.

### Приватный маркетплейс

`add_repo todoltd/claude-methodology-marketplace` (чтение) **отклонён**
классификатором прав сессии. Тексты `odoo19-discovery-*`
(`kickoff-question-builder`, `session-question-builder`,
`discovery-gap-analyzer`, `session-transcript-analyzer`), `tr-*` сверены
только по описаниям в системном списке скиллов и по нашим прошлым разборам.
Выводы «у нас этого нет» для них — **предположение** (принцип №28).

## Ключевые наблюдения

1. Главная ценность — **рамка 2×2** (известное/неизвестное × осознанное/нет)
   и привязка техники к клетке: вопрос лечит только «известное неизвестное»;
   «неизвестное известное» (вкус, узнают на глаз) — показом вариантов;
   «неизвестное неизвестное» — разведкой территории (`blindspot-pass`).
   У нас весь цикл (Q-N, опросники, interview-me) работает с первой клеткой.
2. Их `interview-me` слабее нашего (нет гипотезы с %, догадки, Out of scope,
   явного «да»), но даёт 4 вещи сверх: сортировку по «радиусу поражения»
   (архитектура → поведение → полировка, полировку не спрашивать, а
   предлагать), 2–3 варианта с рекомендацией в каждом вопросе, чекпоинт
   «что уже решили» каждые несколько вопросов, критерий остановки «дешевле
   выяснить при реализации — скажи это вслух», немедленный флаг
   противоречия с прежним решением.
3. Конфликт: у них «you decide» — ответ, который агент берёт на себя;
   у нас «как считаете нужным» — не согласие, а повод дать 2 варианта.
   Наш вариант оставляем: он проверен A/B (+1.00) и для клиента безопаснее.
4. Конфликт имён: их `interview-me` и наш `boost:interview-me` — одно имя.
   Ставить рядом нельзя.

## Вопросы пользователю / решения

- Пользователь не отвечал во время разбора; работал автономно по заданию.
- A/B не проводили (по правилам нужен прогон с разрешения; кейсы описаны в
  `README.md` → «Проверка»).

## Открытые вопросы

- Тексты `kickoff-question-builder`, `session-question-builder`,
  `sales-handover-analyzer`, `tr-functional-requirements`: есть ли в них
  «разведка отрасли» (аналог blindspot-pass) и раздел допущений с
  «сигналом пересмотра»? Нужен доступ к маркетплейсу.
- Сравнить `context-audit` с `skills-janitor` (кандидат B4), когда он будет
  разобран.
