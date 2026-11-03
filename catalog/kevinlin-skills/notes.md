# Рабочий журнал: kevinlin/skills

## 2026-11-03 — старт

- Склонирован `https://github.com/kevinlin/skills` в scratchpad (вне репо),
  коммит `0d3e083` (2026-10-27), 27 коммитов, MIT. Ничего не запускалось.
- Внутри не «один скилл от gap-анализа до кода», а **9 независимых скиллов**
  одним плагином `ai-sdlc-skills` (маркетплейс `ai-sdlc`):
  gap-analysis, spec-coding, research-plan-implement, code-review-expert,
  spec-compact, spec-lint, html-diagram, declawed, agent-insights.
  Фраза из гипотезы («from requirements gap analysis to reviewed, shipped code»)
  — это описание набора, а не цепочки с передачей артефактов.
- Тексты наших `odoo19-discovery-closeout:discovery-gap-analyzer` и
  `odoo19-mvp-build:spec-writer` в контейнере не найдены:
  `~/.claude/plugins/synced/*/` пустой. Попытка подключить
  `todoltd/claude-methodology-marketplace` через `add_repo` отклонена
  классификатором прав. Сравнение пока по описаниям (список скиллов окружения,
  `proposals/siblings-checked.md`) — см. открытые вопросы.

## 2026-11-03 — разбор

Что прочитано целиком: `README.md`, `CLAUDE.md`, манифесты, `versions.json`,
`gap-analysis/SKILL.md` + `references/conventions.md`,
`individual-report.md` (частично), `spec-coding/SKILL.md`, `spec-lint/SKILL.md`
(шаги 1–2, 5.8–5.9, отчёт), `spec-compact/SKILL.md` (шаги 1–3).
Начала прочитаны у `research-plan-implement`, `code-review-expert`,
`declawed`, `agent-insights`.

Безопасность (просмотр импортов и вызовов, ничего не запускалось):
- хуков, MCP, `curl|bash`, установщиков нет; workflows только
  scorecard и dependency-review;
- `agent_insights.py`: stdlib + sqlite3, без сетевых модулей; читает логи
  агентов в домашнем каталоге — в облаке бесполезен, в песочнице сам отказывается;
- `html_to_png.py`: `http.server` на 127.0.0.1 + headless-браузер
  (`--no-sandbox`) через subprocess, только локально;
- `scan.py`: только regex.

Наблюдения:
- `gap-analysis`: версия 1.1.0 в SKILL.md против 1.0.0 в `versions.json`,
  то есть их собственный инвариант синхронизации нарушен.
- `gap-analysis/gap-register.html`: заполненный реестр на 120 разрывов
  (26 Critical, 51 High), упоминания BSC/Zühlke/JARVIS (161), замаскировано
  только «<Project>». Похоже на реальный тендер. Не копируем.
- Активность: первый коммит 2026-07-17 («Initial check»), последний
  2026-10-27, 27 коммитов, один автор, dependabot.

## Открытые вопросы

1. **Нужны тексты** `discovery-gap-analyzer`, `spec-writer`, `tr-review`,
   `track-convergence`. Варианты: пользователь разрешает `add_repo`
   `todoltd/claude-methodology-marketplace` или кладёт тексты в
   `proposals/`. Без них сравнение в items построено на описаниях (№28:
   «не нашёл» не значит «нет»).
2. Делать ли `proposals/odoo19-discovery/gap/` (вставка конвенций) и A/B
   на фикстурах дискавери?
3. Ставить ли задачу `trace-lint` в roadmap (решает главная сессия)?

## 2026-11-03 — правило главной сессии

Пришло сообщение главной сессии (п. 5 `CLAUDE.md`): записывать, что и
откуда берём. В `README.md` добавлены полный SHA, лицензия и раздел
«Что взять» (файл@SHA → что → куда → как → лицензия).
