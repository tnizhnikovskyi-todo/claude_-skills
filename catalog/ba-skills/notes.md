# Журнал разбора: ba-skills

## 2026-11-03, первичный разбор

**Что смотрели.** Клон `uycung/ba-skills` в scratchpad (вне репозитория),
коммит `214f852` (2026-10-26), теги `v1.0.0-vi`, `v1.1.0`. Прочитаны:
`README.md`, все 11 `SKILL.md` (раздел правил целиком), все `references/`
у `requirements-stakeholders` и `requirements-elicitation`,
`templates/elicitation-plan.md`, `scripts/fin.py`, `evals/README.md`
(начало), `.github/workflows/validate.yml`, импорты `evals/run.py`,
`scripts/validate.py`, `evals/grade.py`. Ничего не запускали.

**Гипотеза из поиска подтвердилась:** 11 скиллов БА (стейкхолдеры,
бизнес-кейс, выявление требований, истории и ещё 7: NFR, моделирование,
приоритизация, трассировка, ревью, тест-кейсы/UAT, сборка BRD/PRD/SRS).

**Безопасность.**
- Скиллы — только текст. Единственный скрипт в скиллах:
  `business-case-strategy/scripts/fin.py` (77 строк, stdlib `json`/`sys`,
  читает JSON, печатает ROI/NPV/IRR/payback). Сети, файловой записи нет.
- `evals/run.py` вызывает `claude -p` в tmp-папке; запускается только
  руками, CI его не вызывает. `scripts/validate.py` запускает `fin.py`
  через `sys.executable -I`.
- CI: `permissions: contents: read`, pip `pyyaml`, unittest. Хуков,
  телеметрии, MCP нет.
- Установка через `npx skills add` (сторонний установщик) — нам не нужна,
  если что-то и брать, то текстом.

**Активность.** 47 коммитов за 2026-10-25…26, один автор (Cung Dinh Uy) +
коммиты от Claude. ★0. Есть CI, юнит-тесты грейдера, 31 eval-кейс, 3
открытых issue `skill-quality`. Проект молодой, поддержка не доказана.

**Где наши тексты.** `~/.claude/plugins/synced/*/` пуст в этом контейнере.
Тексты `kickoff-question-builder` / `session-question-builder` взяты из
`proposals/odoo19-discovery/standin/*+INSERT.test.md` (заменитель +
вставка `interview-me`, задача 3.4). Реально доступны в
`~/.claude/skills/synced/*/`: `sales-handover-analyzer`,
`session-transcript-analyzer`, `kickoff-survey-protocol`,
`meeting-protocol-builder`, `tr-*` — их тоже сверяли.

**A/B не делали.** Вердикт «адаптировать» по тексту; прирост — оценка, не
замер.

## Открытые вопросы

1. Нужен ли нам бизнес-кейс (ROI/NPV) вообще: кто его делает в продажах —
   `odoo19-sales-offer`? Если нет, `business-case-strategy` — кандидат на
   отдельный скилл.
2. Применять ли вставки в `odoo19-discovery-*` до получения оригиналов
   скиллов (та же проблема, что в задаче 3.4).
3. Делать ли A/B: kickoff-вопросы с блоком «Стейкхолдеры по чек-листу
   ролей» и без него, на фикстурах `proposals/odoo19-discovery/tests/`.

## 2026-11-03, правило «что и откуда берём»

По сообщению главной сессии (п. 5 `CLAUDE.md` в основной ветке — сверено)
добавил в `README.md` полный SHA, лицензию и раздел «Что взять»: 13 идей с
`путь@SHA`, куда у нас, как (пересказ / только идея / дословно — только
`fin.py`) и разрешение лицензии (MIT, Copyright (c) 2026 Uy Cung).
