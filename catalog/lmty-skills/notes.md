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

1. ~~Дать тексты~~ — закрыто, см. сверку ниже. (Было: включить
   синхронизацию плагинов в среде), чтобы сверить построчно.
2. Разрешить A/B: 6 обезличенных проигранных сделок из журналов продажу
   и 3–4 возражения с защиты КП, прогон «наш скилл» vs «наш + блоки LMTY».
3. Подтвердить: плагин целиком не ставим (сторонний MCP), берём только
   методы в наши `odoo19-sales-*`.

## 2026-11-03, позже

- По сообщению главной сессии (новый п. 5 `CLAUDE.md`) добавлен раздел
  «Что взять» в `README.md`: у каждой идеи `путь@SHA`, что, куда, как,
  лицензия. В карточки `items/` добавлены полный SHA, лицензия, дата.

## 2026-11-03, сверка с нашими текстами

- Главная сессия указала источник: публичный
  `tnizhnikovskyi-todo/sale_todo_claude`. Склонирован в scratchpad,
  коммит `2a7f7c1fa788d42dc734565684885f9c399f9f11`. Прочитаны целиком
  `plugins/odoo19-sales-offer/skills/loss-pattern-analyzer/SKILL.md`
  (380 строк) и `defence-brief/SKILL.md` (438 строк). Текст в наш
  репозиторий не копировался, только ссылки.
- Приватный `todoltd/claude-methodology-marketplace` не понадобился,
  `add_repo` не вызывался.
- **Вывод изменился:** большая часть метода LMTY у нас уже есть.
  Прирост понижен с 2 до 1, итог 11 → 10. Раздел «Что взять» переписан
  на 6 конкретных вставок (см. `README.md`, таблица сравнения).
- Самая полезная находка — побочная: `loss-pattern-analyzer` читает
  чатер без автора и типа сообщения, так что внутренняя заметка продавца
  может засчитаться как «підтверджено чатером». Это прямо противоречит
  его собственному правилу «мітка — гіпотеза сейла».
- Открыто: проверить на живой базе Odoo поля `mail.message.author_id`,
  `message_type`, `subtype_id` и `crm.stage.is_won` для команды ODOO
  (не запускал: нужен запрос к рабочей базе, только с разрешения).
  `demo-build-plan` не сверялся.
