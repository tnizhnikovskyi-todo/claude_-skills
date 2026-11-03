# Рабочий журнал: software-estimation-skills

## 2026-11-03

**Задача от хаба:** разобрать Leanware-io/software-estimation-skills (★0, MIT); гипотеза «3 скилла оценки стоимости с источниками ставок»; сравнить с `preliminary-estimate`, `tr-effort-instruction`; принцип №29.

**Что сделано**
- Клон в scratchpad (вне репо), коммит `e5a989a` (2 коммита всего, оба 2026-11-03, автор Carlos Martinez / Leanware).
- Прочитаны: README, LICENSE, marketplace.json, 3× plugin.json, 3× SKILL.md, все `references/`, `data/savings-2026-10.json` (структура и значения), `prompts/chain.md`, `scripts/build-zips.sh`, `tests/check_table.py`, начало `rates_table.py`, `recalc_check.py`; grep по всем `.py` на сеть/subprocess.
- Пример `examples/customer-portal/`: `rates.md`, `estimate-summary.md`, `savings-summary.md` — цифры согласованы.
- Скрипты **не запускались** (чужой код, разрешения нет).

**Безопасность**
- В скриптах нет `urllib/requests/socket`; `subprocess` — только `soffice --headless --convert-to xlsx` (локально, таймаут 180 с) и вызов соседнего `recalc_check.py`.
- Сеть: только WebSearch самого Claude в `software-market-rates`.
- Хуков, телеметрии, установщиков нет. `build-zips.sh` — только zip.
- Минус: все три SKILL.md требуют дословно закончить ответ рекламой «Sprint 0» Leanware со ссылкой.

**Наши тексты для сравнения — не найдены**
- `~/.claude/plugins/synced/<id>/` пуст; `~/.claude/skills/synced/` содержит tr-review, tr-odoo-tech-design, tr-usecases-acceptance, … но не `tr-effort-instruction` и не `preliminary-estimate`.
- `gh api search/code` по `tr-effort-instruction` и `preliminary-estimate` — 0.
- По всем веткам репо — только упоминания в `proposals/siblings-checked.md` и в заметках `analysis/presales-agent-skill` (та же проблема).
- Косвенно: `tr-review/SKILL.md` чек-лист «Обсяг робіт: усі етапи оцінені, Всього = сума, дано діапазон/допущення»; `tr-odoo-tech-design` → «Далі — tr-effort-instruction (оцінка + інструкція)»; в продажной цепочке «коэффициент вилки».
- Поэтому сравнение в README помечено «сверить» (№28).

## Открытые вопросы

1. Получить тексты `preliminary-estimate` и `tr-effort-instruction` (владелец плагинов / синхронизация) и сверить таблицу «Сравнение» построчно: что из п. 1–6 у нас уже есть.
2. Используем ли мы Claude Code в разработке настолько, чтобы закладывать ИИ-коэффициент в ТР-оценку? Если да — разбирать вместе с `ai-first-estimation` и калибровать на своих фактах.
3. Разрешение на A/B: реальный бриф (обезличенный) → `preliminary-estimate` с/без правил п. 1–4.
4. Нужен ли нам файл ставок с источниками/датами (№29) или ставки фиксирует бухгалтерия и это вне скилла?
