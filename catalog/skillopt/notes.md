# Рабочий журнал: microsoft/SkillOpt

## 2026-11-03 — первичный разбор

**Источник:** https://github.com/microsoft/SkillOpt, коммит `bc0a392`
(2026-10-29), PyPI `skillopt` 0.2.0, MIT. Клон в scratchpad, вне репозитория.
Ничего не запускалось: ни `pip install`, ни оптимизатор, ни тесты, ни
скрипты плагина. Всё ниже по чтению кода и документации.

### Что смотрели

- `README.md`, `docs/guide/training-loop.md`, `docs/guide/skill-document.md`,
  `configs/_base_/default.yaml` — исследовательский цикл (статья
  arXiv 2605.23904).
- `docs/sleep/README.md`, `docs/sleep/RESULTS.md` — SkillOpt-Sleep.
- `plugins/claude-code/` целиком: `plugin.json`, `hooks/hooks.json`,
  `hooks/on-session-end.sh`, `skills/skillopt-sleep/SKILL.md`, `scripts/*.sh`.
- `skillopt_sleep/`: `prompts.py` (все 4 промпта: miner/attempt/judge/reflect),
  `backend.py` (класс Claude, вызов `claude -p`), `consolidate.py` (гейт),
  `gate.py`, `config.py` (дефолты), `budget.py`, `harvest.py` (лексические
  сигналы недовольства), `mine.py` (сплит train/val/test).
- `skillopt/prompts/analyst_error.md`, `skillopt/optimizer/skill_aware.py`
  (SKILL_DEFECT / EXECUTION_LAPSE).
- `ckpt/*/gpt5.5_skill.md` — обученные скиллы из статьи.
- Сеть: grep по `requests|urllib|httpx|urlopen|http(s)://` в `skillopt_sleep/`
  и `plugins/claude-code/`; grep по `telemetry|analytics|sentry|posthog`.

### Проверено

- **Гипотеза «автоматическое улучшение текстов скиллов» подтверждается**, но
  с важной оговоркой: оптимизатор улучшает скилл ПОД МЕТРИКУ на датасете
  задач с проверяемым ответом (SearchQA exact-match, исполнение кода
  SpreadsheetBench и т.п.). Без датасета и грейдера он ничего не делает.
- **Две части.** (1) Исследовательский `skillopt/` — обучение скилла на
  бенчмарке: rollout → reflect → aggregate → select (lr = до 4 правок за
  шаг) → update → gate на val; на границе эпохи slow update и meta skill.
  Дефолт: GPT-5.5 и как оптимизатор, и как цель, Azure OpenAI, 4 эпохи,
  batch 40, 16 параллельных аналитиков. (2) `skillopt_sleep/` — «ночной
  цикл» для своих сессий Claude Code/Codex/Cursor/Copilot: harvest
  транскриптов `~/.claude/projects/*/*.jsonl` + `~/.claude/history.jsonl`
  → LLM-майнер делает 0–3 задачи с проверками на сессию → replay → reflect →
  гейт на val (34% задач) → staging → ручной `adopt`.
- **Гейт.** `gate.py`: кандидат принят, только если его счёт строго выше
  текущего. Опция `gate_no_regression` (по умолчанию выкл.) — ни одна
  val-задача не должна просесть. Метрика `mixed` = 0.5·hard + 0.5·soft.
- **Правки ограничены.** `edit_budget: 4` за ночь; формат
  `{"op":"add|replace|delete","content","anchor","rationale"}`; в Sleep
  правки только дописываются в блок «Learned preferences», старый текст
  удалить нельзя (промпт reflect прямо это говорит). Отклонённые правки
  пишутся в отчёт.
- **Замер слабый для наших скиллов.** Replay (`_ATTEMPT`) — одиночный
  `claude -p` с `--disallowedTools '*'`, ответ до 512 токенов, «Return ONLY
  the final answer text». Т.е. меряется только текст ответа. Скиллы, ценность
  которых в действии (записать файл, задать вопрос до правок, не править
  скилл), так не измерить: промпт reflect даже запрещает правило «спросить
  пользователя». Наш `claude plugin eval` с `tool_used`/файловыми грейдерами
  тут сильнее.
- **Судья.** Для задач без программных проверок — LLM по рубрике, hard = 1,
  если score ≥ 0.8. Майнер сам пишет рубрику и regex-проверки по сессии.
- **Сигналы недовольства** — список фраз на английском (`still wrong`,
  `doesn't work`…), расширяется через `SKILLOPT_SLEEP_NEG_FEEDBACK`.
  Русских фраз нет.
- **Стоимость.** Лимит `max_tokens_per_night: 400_000`, `max_tasks_per_night: 40`.
  Учёт токенов `len(prompt)//4 + len(response)//4` — системный промпт
  Claude Code при `claude -p` (без `--bare`, т.е. на подписке) не
  считается, реальная стоимость выше учтённой. Модель по умолчанию
  `sonnet`. Оценка: десятки–сотня вызовов `claude -p` за ночь, порядок
  единиц долларов на API-ключе. Не мерили.
- **Сеть и телеметрия.** Телеметрии не найдено. Сеть только к выбранному
  провайдеру (через `claude`/`codex` CLI или Azure/OpenAI SDK). В
  `backend.py` захардкожены внутренние Azure-эндпоинты Microsoft
  (`oaidr9.openai.azure.com` и др.) — используются только для бэкенда
  `azure_openai`. Адаптер `superpowers` клонирует `obra/superpowers` (только
  при явном запуске эксперимента). По умолчанию бэкенд `mock` — без сети.
- **Данные.** Сами авторы: «Outbound prompts are not currently guaranteed to
  be secret-free». Обрезанные куски транскриптов уходят провайдеру; есть
  redaction «как defense in depth» и путь «harvest → проверить → `reviewed:
  true` → replay». Плюс локальный `evidence.jsonl` с копиями промптов.
- **Хук плагина** `SessionEnd` (async) — только дописывает строку
  `время\tPWD` в `~/.skillopt-sleep/session-end.log`. Безвреден, но
  always-on. Расписание — через cron (`install-cron.sh`).
- **Облако.** Не подходит: транскрипты `~/.claude/projects` и
  `~/.skillopt-sleep` живут в эфемерном контейнере, cron не переживёт
  контейнер, нужен `pip install skillopt` (чужой установщик).
- **Обученные скиллы** (`ckpt/`) — 300–2000 слов узких правил под формат
  бенчмарка (SearchQA: «сохраняй прямой апостроф», «единственное число
  в кроссвордных ответах»). Это подгонка под exact-match, а не метод;
  наш лимит `SKILL.md` ≤ ~150 строк они бы нарушили.
- **Свидетельство в пользу гейта** (`RESULTS.md` §1): без гейта
  GPT-5.4-nano на SearchQA 0.554 → 0.026 за 5 ночей (оптимизатор выучил
  «отвечай заголовком документа»), с гейтом 0.570 → 0.570. Это прямое
  подтверждение нашего правила «без положительной разницы не сливать».
- **Активность.** 593 коммита с 2026-05-21, 92 автора, 23 коммита в
  октябре, последний 2026-10-29; Microsoft Research, есть CI и сотни тестов.

### Сравнение с нашим циклом

См. `items/skillopt-sleep.md` и `items/skillopt-core.md`, раздел «Что
перенести» в `README.md`.

### Открытые вопросы

- Реальный A/B не делали (нужно разрешение и бюджет). Если захотим — только
  бэкенд `mock` (без сети) на синтетике или `--tasks-file` с нашими
  кейсами, на отдельной машине, не в рабочем репозитории.
- Стоит ли главной сессии майнить замечания из транскриптов облачных
  сессий через `list_events` (аналог harvest)? Решение пользователя: дорого
  и затрагивает приватность.
