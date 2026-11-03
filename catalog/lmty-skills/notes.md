# Журнал разбора `lmty-skills`

## 2026-11-03

- Клонирован `LMTYdotcom/skills` в scratchpad (вне репо), коммит
  `18667e0` (2026-11-01). Ничего не запускалось: ни `scripts/*.py`,
  ни MCP-сервер, ни установка плагина.
- Состав: 16 скиллов `competitive-*`, `shared-references/` (6 общих
  файлов), манифесты под Claude Code / Codex / Gemini / Agent Plugins,
  CI (validate, links, scorecard, release, live-install), dependabot.
  193 файла, 17 коммитов: релиз 1.0.0 2026-09-28, правки до 2026-10-02,
  потом только dependabot.
- **Сеть:** `.mcp.json` → `https://mcp.lmty.com/mcp` (HTTP, OAuth). При
  установке плагина сервер подключится сам. По `shared-references/lmty.md`
  инструменты только чтение (`list_products`, `list_competitors`,
  `get_report(section)`, `get_report_changes(limit 1..50)`,
  `get_evidence`, `get_freshness` …). Код сервера закрыт, проверить нельзя.
- Хуков нет. Исполняемого кода в скиллах нет. `scripts/build_skills.py`
  копирует shared-references в каждый скилл (md5 `TRUST.md` одинаковый
  у всех 16).
- Размер: описания всех 16 ≈ 9.8 КБ (всегда в контексте), `SKILL.md`
  ≈ 180 КБ в сумме, `references/` ≈ 544 КБ (≈34 КБ на скилл).
- Прочитаны целиком: `competitive-battlecard`, `competitive-win-loss-analysis`
  (+ METHODOLOGY, шаблон), `shared-references/trust-and-evidence.md`,
  `lmty.md`; по шагам: `deal-prep`, `objection-response`, `poc-rfp-plan`.
  Остальные — по описанию в README и frontmatter.
- Гипотеза «battlecards, win-loss, позиционирование, ценообразование»
  подтверждена; набор ориентирован на PMM SaaS-компании.

## Сравнение с нашими скиллами

- `~/.claude/plugins/synced/*/` в этом контейнере **пуст**; `ListPlugins`
  по `sales-offer`/`defence`/`loss` ничего не вернул; поиск по
  `org:todoltd` 0 результатов. Тексты `odoo19-sales-offer:defence-brief`
  и `loss-pattern-analyzer` прочитать не удалось.
- Сравнение сделано по месту скиллов в цепочке
  (`proposals/siblings-checked.md`): `offer-finalizer → defence-brief →
  defence-debrief`; `loss-pattern-analyzer` читает журнал продажу.
  Выводы о различиях помечены UNVERIFIED.

## Открытые вопросы к пользователю

1. Дать тексты `defence-brief` и `loss-pattern-analyzer` (или включить
   синхронизацию плагинов в среде), чтобы сверить построчно.
2. Разрешить A/B: 6 обезличенных проигранных сделок из журналов продажу
   и 3–4 возражения с защиты КП, прогон «наш скилл» vs «наш + блоки LMTY».
3. Подтвердить: плагин целиком не ставим (сторонний MCP), берём только
   методы в наши `odoo19-sales-*`.

## 2026-11-03, позже

- По сообщению главной сессии (новый п. 5 `CLAUDE.md`) добавлен раздел
  «Что взять» в `README.md`: у каждой идеи `путь@SHA`, что, куда, как,
  лицензия. В карточки `items/` добавлены полный SHA, лицензия, дата.
