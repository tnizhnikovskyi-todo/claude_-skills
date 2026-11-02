# graphify: рабочий журнал

## 2026-11-02, старт

- Склонирован `https://github.com/Graphify-Labs/graphify` в scratchpad
  (вне репо), коммит `32e5efe` от 2026-11-01, тег `v1.0.0`.
- Ничего из внешнего репо не запускалось: только чтение.
- Активность: 2727 коммитов с 2026-04-04, 704 коммита за октябрь 2026.
  Основной автор Safi Shamsi (`safishamsi`), ~1250 коммитов; ещё десятки
  контрибьюторов. Компания Graphify Labs (YC S26), есть платный Graphify Cloud.
- Пакет на PyPI: `graphifyy` (две y). Остальные `graphify*` не их.

## 2026-11-02, первичный разбор

Что прочитано: `README.md`, `ARCHITECTURE.md`, `BENCHMARKS.md` (выборочно),
`SECURITY.md`, `pyproject.toml`, `LICENSE*`/`NOTICE`, `graphify/skill.md`,
`graphify/always_on/claude-md.md`, в коде: `install.py` (что пишется в
`~/.claude` и `.claude/settings.json`), `cli.py` (`_run_hook_guard`, тексты
подсказок), `llm.py` (`detect_backend_with_source`, `claude -p`),
`querylog.py`, `serve.py` (список MCP-инструментов, HTTP-авторизация),
`hooks.py` (git-хуки), `prs.py` (вызов `gh`).

Проверки grep'ом по `graphify/*.py`:
- `shell=True`, `eval(`, `exec(` — не найдено.
- Сетевые адреса: только API LLM-провайдеров (`llm.py`), arXiv/oEmbed
  (`ingest.py`), CDN в генерируемом HTML, `gh` CLI. Своего домена для
  телеметрии/проверки обновлений нет; app.graphify.com только печатается.
- Лог запросов: в коде opt-in (`GRAPHIFY_QUERY_LOG_ENABLE=1`), README
  утверждает, что включён по умолчанию — устаревшая документация.
- XML (`.xml`) в списке «секретоопасных» data-расширений, AST-экстрактора
  для XML нет → вью Odoo пойдут в LLM-проход или выпадут. `odoo` в коде не
  упоминается, `_inherit = 'model.name'` (строка) Python-AST как наследование
  не распознает. Гипотеза, проверить запуском.

Наблюдения:
- Скилл: 797 строк; Step 1 сам делает `uv tool install --upgrade graphifyy`
  (или `pip install --break-system-packages`), если пакет не найден.
- Семантический проход в Claude Code — `general-purpose` субагенты, все в
  одном сообщении; при `GEMINI_API_KEY` — Gemini.
- Хуки: `Bash|Grep` → `hook-guard search`, `Read|Glob` → `hook-guard read`;
  strict-режим один раз за сессию делает `deny` на Read.
- Бенчмарк по коду: ERPNext, n=6, 82.0% vs 70.8% grep/read, ~140K токенов
  на вопрос. Остальные бенчмарки про память диалогов.

Решения: оценка 11/18, вердикт «адаптировать» (см. `README.md`).

## Открытые вопросы

1. Разрешит ли пользователь установить `graphifyy` (пин версии) в
   изолированный venv и прогнать `graphify extract --code-only` на тестовом
   репо? Без этого «Проверка» пустая.
2. На каком репо испытывать: наш Odoo-модуль `td.*` или кусок Odoo core?
3. Нужен ли нам вообще граф по документам (PDF/ТР) — это уже LLM-проход и
   токены.
