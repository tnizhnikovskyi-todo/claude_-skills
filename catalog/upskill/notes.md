# Журнал разбора: huggingface/upskill

## 2026-11-03

**Что смотрели.** Клон `https://github.com/huggingface/upskill` в scratchpad
(вне репозитория), коммит `eec8ab46f970a880e4d21cfd41dff50ac08c6847`
(2026-10-14). Ничего не запускали: ни `uv`/`pip`, ни тесты, ни
`propose-skills.sh`, ни `scripts/hf/*.sh`.

**Прочитано целиком:** `README.md`, `LICENSE`, `pyproject.toml`,
`upskill.config.yaml`, `fastagent.config.yaml`,
`src/upskill/agent_cards/{skill_gen,test_gen,evaluator}.md`,
`src/upskill/generate.py`, `evaluate.py`, `verifiers.py`, `ci.py`,
`models.py` (с 455 по 614 строку), `tests/fixtures/ci_action_repo/*`,
`tests/test_agent_card_guardrails.py`.
**Прочитано выборочно (grep + фрагменты):** `cli.py` (2392 строки:
`_load_trace_context`, `_create_generate_skill_record`,
`_run_generate_refinement_loop`, список команд), `hf_jobs.py`,
`executors/local_fast_agent.py`, `scripts/hf/job_entrypoint_fast_agent.sh`,
`propose-skills.sh` (строки 1–60 и grep по `claude`, `history`, `jsonl`).

**Лицензия.** Сам файл `LICENSE`: Apache License 2.0, «Copyright 2026
Hugging Face». В `pyproject.toml` поля license нет; чужих файлов с другой
лицензией (vendored) в дереве нет, все файлы — код проекта, тесты и
конфиги. Поиск (Apache-2.0) совпал с файлом.

**Активность.** 89 коммитов, 2026-01-21 → 2026-10-14. Авторы: evalstate
(51), burtenshaw (17), shaun smith (14). Последняя функциональная работа —
2026-03/05 (v2: HF Jobs, верификаторы, заготовка CI); после этого только
коммиты бота безопасности HF (пины Actions, права `GITHUB_TOKEN`).
~761 звезда (по `candidates-2026-11-03-search.md`).

## Находки по коду

1. **Генерация скилла** (`generate.py`, `agent_cards/skill_gen.md`): один
   промпт «Create a skill document that teaches…» + 3 few-shot примера;
   тело 200–400 слов, description < 100 символов. Нет `references/`,
   нет скриптов («treating these as future»), нет поля «когда НЕ
   использовать».
2. **Генерация тестов** (`generate.py`, `TEST_GENERATION_PROMPT`): 3–5
   кейсов по ОДНОМУ описанию задачи (скилл генератору тестов не
   показывают), в каждом ≥ 2 строки в `expected.contains`; иначе
   предупреждение. Негативных кейсов (где скилл не должен срабатывать)
   нет.
3. **Проверка** (`verifiers.py`): `contains` — подстрока без учёта
   регистра; `file_exists`, `file_contains`; `command` —
   `subprocess.run(cmd, shell=True, cwd=workspace, timeout=60)`; legacy
   `validator`. LLM-судьи в `generate`/`eval` нет (поле `judge` есть
   только в моделях CI).
4. **A/B** (`evaluate.py`): одни и те же кейсы прогоняются «with-skill»
   и «baseline» (без скилла), метрики: доля успешных, токены, ходы.
   `skill_lift = with − base`; `is_beneficial = lift > 0.05 или (lift ≥ 0
   и токенов на 20% меньше)` (`models.py:467-470`).
5. **Цикл улучшения** (`cli.py:709-797`): до `max_refine_attempts` (2)
   попыток; стоп, если `is_beneficial` или прирост между попытками
   < 0.05 («Plateaued»). В промпт правки (`refine_skill`) идут первые 500
   символов тела и 3 провала, **включая ожидаемые строки грейдера**
   (`get_failure_descriptions` добавляет `Expected: …`). Итоговый прирост
   считается на тех же кейсах, по которым правили — отложенной выборки
   нет.
6. **Учитель/ученик**: `--model` генерирует и правит, `--eval-model`
   (например haiku) — отдельный прогон на дешёвой модели; `eval -m haiku
   -m sonnet --runs 5` — матрица моделей. В режиме benchmark (несколько
   моделей или `--runs > 1`) baseline **выключен**.
7. **Системный промпт обеих рук** (`agent_cards/evaluator.md`): «You are
   an evaluator of skills… return a score» — тестируемой модели говорят,
   что она оценщик. Странная рамка, одинаковая для обеих рук, но
   искажает задачу.
8. **CI-заготовка** (`ci.py`, `models.py`): манифест `.upskill/evals.yaml`
   со сценариями (набор скиллов + файл кейсов + judge + baseline);
   выбор сценариев по `git diff --name-only base...HEAD` → ближайшая папка
   с `SKILL.md`; отчёт с вариантами bundle / ablation (без одного скилла) /
   baseline и таблицей вклада (`hard_score_delta`, `judge_score_delta`,
   `passed_without_skill`); вывод в `GITHUB_STEP_SUMMARY`. **Команды
   `upskill ci` в `cli.py` нет** (команды: generate, eval, list,
   benchmark, runs, plot) — есть только хелперы и тесты.
9. **Из трейса** (`cli.py:582-593`): `--from trace.md|json` — первые 4000
   символов трейса дописываются к задаче.
10. **`propose-skills.sh`**: читает `~/.claude/projects/**/*.jsonl` за 30
    дней, берёт до 50 уникальных сообщений пользователя, шлёт их в
    `claude -p` с просьбой предложить 3–5 скиллов, генерирует `SKILL.md`
    в `~/.claude/skills` (глобально, по умолчанию).

## Права, сеть, данные

- **Локально:** `upskill` ставится через `uv pip install upskill`
  (PyPI), зависимость `fast-agent-mcp>=0.6.7` без верхней границы;
  оценка шеллит `fast-agent go` в `runs/<batch>/…/workspace`. Модель —
  через ключи провайдера (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`,
  `generic` для локальных).
- **HF Jobs:** в репозиторном `upskill.config.yaml` `executor: jobs` и
  `jobs_secrets: HF_TOKEN,ANTHROPIC_API_KEY`: ключи пробрасываются в
  удалённый контейнер HF Jobs (`ghcr.io/astral-sh/uv:python3.13-bookworm`),
  скилл + кейсы + выводы загружаются в датасет-репозиторий HF
  (`--artifact-repo`), приватность которого задаёт пользователь. Дефолт в
  коде (`config.py:137`) — `local`; `jobs` включает именно файл-пример.
- **Телеметрии** в коде upskill нет (grep `telemetry|posthog|analytics`
  пусто); у `fast-agent` отдельно не проверяли.
- **Исполнение кода из файла кейсов:** верификатор `command` с
  `shell=True` — файл тестов фактически исполняемый.

## Сравнение с нашим

- `claude plugin eval` уже делает то же A/B «с плагином/без», но в
  настоящем Claude Code (инструменты, триггер по `description`, хуки) и с
  LLM-судьёй; upskill меряет в харнессе fast-agent, где скилл подложен
  через `--skills-dir`, триггер Claude Code не проверяется.
- Наши правила сильнее: ≥ 3 кейса с негативным, грейдеры «результат, а не
  слова», негативный/позитивный контроль, `--runs 3`.
- `skill-creator` (по описанию в списке скиллов): evals, benchmark с
  дисперсией, оптимизация `description` под триггер — покрывает
  генерацию+оценку лучше для Claude Code.
- `skill-feedback` + `weekly-review.md`: у upskill аналога нет (нет
  наблюдений пользователя, только синтетика).
- skillopt (правка принимается только по отложенной выборке) прямо
  показывает, чем плох цикл upskill (п. 5).

**Чего у нас нет и стоит взять:** вклад каждого скилла в составе
плагина (leave-one-out + `passed_without_skill`), выбор кейсов по
изменённым папкам скиллов, ветка «качество то же, токенов −20%» в
правиле принятия, матрица «скилл × модель» (дешёвая модель как ученик),
стоп по плато.

## Открытые вопросы

1. Умеет ли `claude plugin eval` отключать по одному скиллу внутри
   плагина (в `evals/README.md` упомянут `--ablation none`) и выбирать
   модель агента? Проверить у `claude-code-guide` / `--help` до задачи.
2. Нужен ли A/B на Sonnet/Haiku: какие наши скиллы реально запускаются
   на дешёвых моделях (субагенты, задачи по расписанию)?
3. Майнинг кандидатов в скиллы из истории (`propose-skills.sh`) в облаке
   возможен только через `list_events` — решение пользователя (то же
   открыто в skillopt).
