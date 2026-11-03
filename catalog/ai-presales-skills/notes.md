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

### Ограничение сравнения
- Тексты наших `odoo19-sales-*` в окружении не найдены
  (`~/.claude/plugins/synced/…` пуст; то же отмечено в
  `proposals/siblings-checked.md`). Сравнение по стадиям делаем по цепочке
  скиллов и описаниям из `proposals/siblings-checked.md`. По принципу №28
  «не нашёл ≠ нет»: всё, что помечено «у нас нет», надо сверить с самими
  текстами, когда они будут доступны.
- A/B не проводили: вердикт «взять» не ставится.

## Открытые вопросы
- Есть ли у нас теги уверенности в брифе/журнале (реестр G-N «гипотезы»?)
  и шлюз go/no-go перед демо? Проверить по текстам `odoo19-sales-prep`.
- Нужен ли нам аналог `rfx-navigator-presales` для тендеров (Prozorro и
  т. п.)? Спросить пользователя о частоте тендеров.
