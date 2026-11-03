# Журнал разбора: caliper

## 2026-11-03

**Задача от главной сессии:** сравнить методику Caliper (кейсы, повторы,
судья, статистика, стоимость, шум, MCP) с нашим `claude plugin eval`
(`plugins/boost/evals/README.md`, `reports/`), найти, что перенести в правила.

### Что смотрели

- Клон `edonadei/caliper` в scratchpad, `89ab3b0` (2026-11-01), 318
  коммитов с 2026-05-12, v0.21.0, теги до v0.9.1 (дальше без тегов).
- `LICENSE` — MIT, Emrick Donadei 2026. Сторонних файлов с другой
  лицензией нет; `uv.lock` — только зависимости.
- Прочитаны: `README.md`, `docs/results.md`, ADR 0001, 0006, 0007, 0013,
  0026, 0027, 0028; `caliper/compare.py` (предупреждения, регрессия),
  `judge/eval_judge.py` (промпт судьи, режим скрипта),
  `harness/claude_code.py` (флаги запуска), `activation.py`,
  `docs/telemetry.md`, `telemetry.py` (хост PostHog), `pyproject.toml`,
  `skills/grill-skill/SKILL.md`. Остальные ADR и харнессы Codex/Pi/Hermes —
  по заголовкам.
- Наше: `evals/README.md`, `reports/independent-check.md`,
  `reports/cbm-pilot.md`, `reports/foundation.md` (шум), сводки `skillopt`,
  `arena-skill`, `one-skill-to-rule-them-all`, `synthesis.md`.

### Что проверили

- **Интервалов нет.** Поиск `wilson|confidence|interval|bootstrap|variance`:
  только комментарий в `compare.py:356` («интервалы должны быть на балле»).
  `compare` помечает любое падение, выход не валит; код выхода 3 «планка не
  взята» зарезервирован, но не реализован.
- **Опасные умолчания:** `--dangerously-skip-permissions` в каждой попытке
  (`claude_code.py:283`); настройки и коннекторы пользователя грузятся по
  умолчанию (ADR 0028 заменил изоляцию 0026); ADR 0027 «попытка не граница
  безопасности».
- **Судья исполняет код:** режим `script` — Python с `assert`, запускается
  в рабочей папке попытки.
- **Телеметрия:** PostHog, opt-out, без содержимого; первый запуск ничего
  не шлёт; в CI выключена.
- **Наши числа через Уилсона** (свой расчёт, `python3 -I`): 9/9 →
  0.70–1.00, 6/9 → 0.35–0.88. Вывод: +0.11 (`odoo-model-map`) и +0.23
  (`repo-audit`) при n=9 не отличимы от шума; +1.00 и +0.45 устойчивы.

### Сравнение с прошлыми разборами

- `skillopt`: гейт на отложенной выборке и no-regression по кейсу. Caliper
  дополняет: «держится» = сравнение с прошлым полным прогоном; регрессия
  «any-below» по задаче — то же, что no-regression по кейсу.
- `arena-skill`: шум судьи за 7 раундов; Caliper борется с шумом иначе —
  типизация исходов и подтверждение на k≥5.
- `one-skill`: №28 «отсутствие не доказывается поиском» — совпадает с
  принципом Caliper «`activated: null`, а не `[]`, когда наблюдать нельзя».

### Ничего не запускали

Ни CLI, ни скиллы, ни тесты (п. 3 `CLAUDE.md`).

### Открытые вопросы

1. Умеет ли `claude plugin eval` отключать MCP-сервер в одном плече (для A/B
   Context7)? Если нет — разовый прогон Caliper с
   `--no-user-customizations` и `CALIPER_TELEMETRY_DISABLED=1`, только с
   разрешения пользователя.
2. Есть ли в `claude plugin eval --json` баллы по отдельным прогонам (для
   порога шума) — проверить на любом сохранённом `--json`.
3. Принять ли черновик `evals-rules-draft.md` в `evals/README.md` целиком
   или частично — решает главная сессия.
