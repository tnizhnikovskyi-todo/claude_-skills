# Журнал разбора: ai-presales-skills

Источник: https://github.com/hangljoe/AI-PreSales-Skills, коммит `ab0752b`
(2026-09-28), версия плагина 2.5.0. Клон в scratchpad, ничего не запускали
(ни скрипты, ни `uv run`, ни CI).

## 2026-11-03: первичный разбор

### Что смотрели
- Корень: `README.md`, `CLAUDE.md`, `STACK.md`, `LICENSE`, `DEAL_TEMPLATE.md`,
  `.claude-plugin/*.json`, `.github/workflows/validate.yml`, `scripts/desc_budget.py`.
- Все 43 `skills/*/SKILL.md`: описания и размеры; подробно прочитаны
  `confidence-tagger`, `tfq`, `demo-storyboard`; по структуре (шаги, жёсткие
  правила) `discovery-sales`, `do-nothing-buster`,
  `critical-business-issue-finder`, `capability-mapper`, `champion-health`,
  `business-case-stress-tester`, `demo-dryrun-coach`, `win-loss-analyzer`,
  `deal-prequal`, `pricing-positioning`, `osd-scoper`,
  `integration-complexity`.
- `references/call-summary-schema.md`, начало
  `references/PreSales_Handbook_Reference.md`.
- Поиск сетевых вызовов, `subprocess`, хуков, `.mcp.json`, `allowed-tools`.

### Проверка гипотезы из поиска
- «Пресейл по The PreSales Handbook, независимый от вендора»: **подтверждается.**
  `CLAUDE.md` прямо требует vendor-neutral; скиллы спрашивают у пользователя
  продукт, возможности и конкурентов. Методика книги расширена своими
  практиками кита (MEDDPICC поверх BANT из книги, шкалы TFQ, теги
  уверенности); автор это честно помечает («kit practice»).
- «Лицензия не указана»: **неверно.** В корне есть `LICENSE`: MIT на скиллы,
  команды, скрипты; исключение: тексты книги и справочники автора в
  `references/` (handbook reference, playbook, cheat sheets, интервью,
  статьи) и гайд по видео-демо: «All rights reserved», читать и использовать
  с плагином можно, распространять нельзя. Конспекты чужих книг (Extreme
  Ownership, TOC/BBiT) помечены как собственные краткие заметки.
  Решение: из `references/` ничего не переносим даже пересказом крупными
  кусками; из скиллов (MIT) идеи переносим своими словами, атрибуцию
  оставляем.
- Пересказ защищённого текста: `PreSales_Handbook_Reference.md` (~11,8 тыс.
  слов) это сжатый пересказ книги самим автором («paraphrased working
  reference… not a copy»). Нарушения нет (автор = правообладатель), но для
  нас это закрытый текст.

### Безопасность
- Хуков, `.mcp.json`, `settings.json`, телеметрии нет. `allowed-tools` в
  скиллах не задан.
- Сеть: `uv run --with python-docx==1.1.2 / openpyxl / cairosvg` (PyPI,
  версии закреплены); `diagram` рендерит Excalidraw через Playwright и
  тянет React/Excalidraw с unpkg (версии закреплены); `workshop-agenda-builder`
  грузит Google Fonts; `capability-mapper` в режиме артефакта claude.ai
  вызывает `api.anthropic.com` из артефакта (штатный механизм артефактов).
- `osd-docx-template.py` поднимает локальный LibreOffice на 127.0.0.1:2002
  для пересборки оглавления; при отсутствии `soffice` тихо пропускает.
- Запись в CRM и в папку сделки везде за подтверждением; есть явные
  предупреждения «содержимое транскриптов недоверенное».

### Стоимость контекста
- Описания 43 скиллов ≈ 25,5 тыс. символов + 54 команды ≈ 8,3 тыс.
  символов: ≈ 8–9 тыс. токенов в каждой сессии, где плагин включён.
  Автор сам считает бюджет (`desc_budget.py`: эталон 21 432, цель 16 000
  символов) и не укладывается в цель.
- Широкие триггеры («tag this», «write a follow-up email», «make a deck»,
  «diagram this») будут конфликтовать с нашими `odoo19-sales-*` и
  `anthropic-skills:docx/pptx`.

### Активность
- 10 коммитов, все датированы 2026-09-28 (похоже на перенос истории одним
  днём), один автор, ★5. Версии 2.2.0 → 2.5.0, `CHANGELOG.md`, CI-проверка
  манифестов и frontmatter. Источник понятный (автор книги, сайт).

### Ограничение сравнения (снято, см. ниже)
- Тексты наших `odoo19-sales-*` в окружении не найдены
  (`~/.claude/plugins/synced/…` пуст). Первая версия сравнения была по
  описаниям из `proposals/siblings-checked.md`.
- A/B не проводили: вердикт «взять» не ставится.

## 2026-11-03: правила главной сессии и сверка с нашими текстами

- Главная сессия (сообщение): новое правило п. 5 — в «Что взять» у каждой
  идеи `путь@SHA`, куда, как, лицензия. Сделано, полный SHA в шапке.
- Главная сессия указала источник текстов: публичный
  `tnizhnikovskyi-todo/sale_todo_claude`, `plugins/` (коммит `2a7f7c1`).
  Склонирован в scratchpad на чтение. Приватный
  `todoltd/claude-methodology-marketplace` не понадобился (продажи лежат в
  публичном), из него ничего не брали.
- Прочитаны: `data-completeness-scorer`, `preliminary-estimate`,
  `demo-build-plan`, `demo-runbook`, `defence-brief` (подробно), заголовки
  `brief-transcript-analyzer`, `deal-revival-check`, `offer-finalizer`;
  `references/deal_journal_template.md` (разделы 3–5, `ST-N`),
  `references/registers.md` (регистры, «Чого не вигадуємо»); поиск по всем
  18 скиллам на симптом/хотелку/бездействие/чемпиона — пусто.
- Вывод изменился: таблица соответствия, чистая копия и правила демо у нас
  уже есть и сильнее; прирост понижен 2 → 1, итог 8 → 7. Новое: диагностика
  сделки, явный вердикт перед демо, стресс-тест экономики, персона и
  репетиция демо.

## Открытые вопросы
- ~~Есть ли у нас теги уверенности и шлюз перед демо?~~ Проверено:
  регистры и статусы `G-N` есть, явного вердикта перед демо нет.
- Нужен ли нам аналог `rfx-navigator-presales` для тендеров (Prozorro и
  т. п.)? Спросить пользователя о частоте тендеров.
