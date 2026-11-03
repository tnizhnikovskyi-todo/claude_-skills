# ECC — рабочий журнал

## 2026-11-03

### Что склонировали
- `affaan-m/ECC`, `main` @ `b38be6a7f6350964d59328b52f0624e1d1d552d1`
  (2026-10-29), версия 2.2.3. Клон в scratchpad, вне репо. Ничего не
  запускали (скрипты, `install.sh`, хуки, MCP, `npx`).
- Для проверки активности догрузили историю без блобов
  (`git fetch --filter=blob:none --depth=10000`): 4321 коммит.

### Популярность: накрутка или нет
- Поиск GitHub: 296 302 ★, 43 824 форка, создан 2026-01-18, последний пуш
  2026-11-02, 216 открытых issues/PR. Всего issues 940, слитых PR 1345.
- История: 4321 коммит, 517 разных авторов; помесячно 78 (янв) → 569
  (мар) → 134 (июл) → 955 (окт). Основные: Affaan Mustafa 1636+141,
  `haelyra` 665 (в октябре 64 из 100 последних коммитов), далее десятки
  внешних авторов с 30–100 коммитами.
- Issues содержательные (баги хуков на Windows, обход gateguard через
  `.claude/settings*.json`, пропуски редактирования секретов), но много и
  мусорных «[Copilot]» без текста — признак широкой случайной аудитории.
- Форки/звёзды ≈ 15% — для накрутки нетипично (у купленных звёзд форков
  почти нет). Звездочётов через API проверить не смогли (доступ к API
  репозитория у сессии закрыт, работает только поиск).
- Вывод: активность настоящая, проект живой; 296 тыс. ★ за 10 месяцев —
  вирусная популярность (хайп вокруг «полного набора для Claude Code»),
  а не мерило качества. Звёзды как сигнал пользы игнорируем.

### Лицензия
- Корневой `LICENSE`: MIT, © 2026 Affaan Mustafa.
- Внутри есть файлы под другими лицензиями (frontmatter `license:`):
  CC-BY-SA-4.0 — `skills/osint-investigation` (свой `LICENSE.txt`);
  Apache-2.0 — 8 скиллов логистики/производства
  (`customs-trade-compliance`, `returns-reverse-logistics`,
  `carrier-relationship-management`, `energy-procurement`,
  `production-scheduling`, `logistics-exception-management`,
  `quality-nonconformance`, `inventory-demand-planning`);
  `skills/context-and-decisions/LICENSE` — MIT, © Matt Pocock.
- `gateguard` — `origin: community`, код ссылается на
  `github.com/zunoworks/gateguard`; `santa-method` — автор Ronald Skelton
  (RapportScore.ai). Для них лицензия = MIT корня, но атрибуцию автору
  сохраняем.

### Перечень и стоимость (подсчёт по исходникам)
- 314 `SKILL.md` (82 тыс. строк), описания 102 тыс. символов; агенты 71
  (16 тыс. символов описаний), команды 98 (14 тыс.). Подсчёт скриптом по
  frontmatter, символы/4 ≈ токены.
- `rules/common` 19.4 КБ, `rules/python` 4.8 КБ — ставятся установщиком в
  `~/.claude/rules` (плагином не ставятся).
- `hooks/hooks.json`: 28 регистраций (PreToolUse 10, UserPromptSubmit 1,
  PreCompact 1, SessionStart 2, PostToolUse 2 диспетчера,
  PostToolUseFailure 2, Stop 8, SessionEnd 1). Профили `minimal/standard/
  strict` через `ECC_HOOK_PROFILE`, `hooks_enabled` по умолчанию `true`.
- `session-start.js`: контекст старта ≤ 8000 символов, ≤ 6 инстинктов.

### Сеть и телеметрия
- `grep` по `scripts/hooks` и `scripts/lib`: внешних URL в вызовах нет;
  `http.request` только к локальному Plan Canvas. Ссылки на спонсоров
  (`compute-sponsor.js` → compute.itomarkets.com, Nasiko) — текст в CLI.
- Метрики стоимости → `~/.claude/metrics/costs.jsonl` (локально).
- Наблюдатель инстинктов: `claude --model haiku --print` раз в 5 мин,
  по умолчанию выключен.
- Не нашли в хуках `git pull`/`npm install`/`curl` (автообновления нет).

### Сверка с нашими скиллами
- `tr-usecases-acceptance` (синхронизированная копия в
  `~/.claude/skills/synced/...`): Given/When/Then, нет «не повинно» и
  метода проверки → вставка 1 обоснована.
- `session-transcript-analyzer`: реестры D/X/C/T/Q/A, глоссария нет →
  вставка 2 обоснована.
- gstack (`origin/analysis/gstack`, summary): похожий вывод — отклонить
  установку, брать методы; у gstack 5.5 тыс. токенов на вызов, у ECC
  33 тыс. в каждой сессии.

### Отбор (8 карточек из ~480 файлов-инструкций)
Смотрели также и не взяли: `verification-loop` (npm/tsc-ориентирован,
дублирует `code-review`), `skill-stocktake` (≈ `automation-audit`),
`strategic-compact`/`context-budget` (встроенные `/context`, автокомпакт),
`delivery-gate` (блок по свободному месту на диске и «свежести» журналов —
не про нас), `recursive-decision-ledger` (трейдинг), `brownfield-retrospective`
(веб-SDLC, тяжёлый), `master-agreement-generator` (DRAFT-договоры из
шаблона — у нас КП в `odoo19-sales-offer`), `lead-intelligence` (X API,
Exa), агенты `silent-failure-hunter` (≈ наш «Пол качества»), `spec-miner`
(OpenSpec, у нас ТР → SPEC).

### Открытые вопросы
- Поднимается ли `chrome-devtools-mcp` из корневого `.mcp.json` при
  установке плагина (в `plugin.json` `mcpServers: {}`) — не проверяли.
- Лицензия первоисточника gateguard (`zunoworks/gateguard`) — не смотрели;
  берём только идею, поэтому не блокирует.
- A/B для вставок 1–5 — в сессиях реализации.
