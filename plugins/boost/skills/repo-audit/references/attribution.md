# Атрибуция

Скилл `repo-audit` адаптирован из скилла `ponytail-audit` плагина
**ponytail** (https://github.com/dietrichgebert/ponytail, v5.3.3, коммит
`96608e0`, файл `skills/ponytail-audit/SKILL.md`; формат находки сверен с `skills/ponytail-review/SKILL.md`). Разбор: `catalog/ponytail/`
в репозитории `tnizhnikovskyi-todo/claude_-skills`.

Что взято (переведено и сокращено): порядок «карта → потоки → поиск по 6
категориям → проверка находки конкретным случаем → ранжированный отчёт»,
4-частный формат находки (что это / проблема / фикс / если не чинить),
сквозная нумерация, лимит 20 находок, `Verdict`/`Lean`/`Not checked`.

Что изменено: отчёт на русском, добавлен шаг карты для модуля Odoo и
чек-лист `references/odoo-checklist.md` (права доступа, `ir.rule`,
контроллеры, `sudo()`, cron, стандартные механизмы Odoo 19). Не перенесено:
хуки, band, always-on инъекции.

## Лицензия оригинала

MIT License

Copyright (c) 2026 DietrichGebert

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Дополнения (boost-pass4, 2026-11-03)

- **`references/odoo-dead-code.md`** — пересказ своими словами чек-листа
  ложно «мёртвого» кода Odoo и классов «мёртв / подозрителен / ложное
  срабатывание» из
  [focuz-ai/odoo-spec-kit](https://github.com/focuz-ai/odoo-spec-kit)
  `ai-specs/skills/odoo-code-auditing/references/dead-code-methodology.md@23df08b`
  (MIT, © 2026 Focuz AI); сам файл — Odoo-переработка
  [jeffrigby/somepulp-agents](https://github.com/jeffrigby/somepulp-agents)
  `plugins/codebase-health/skills/code-auditing/references/dead-code-methodology.md@e56195b`
  (MIT). Текст не копировался; таблица, миграции, миксины и правило «поле
  не существует» добавлены нами. Разбор: `catalog/odoo-spec-kit/README.md`, п. 1.
- **«Утверждение — доказательство»** (шаг 3) — пересказ «Claims Need
  Evidence» (`investigate/sections/preamble.md@7caca33`) и «Pre-emit
  verification gate» (`review/SKILL.md@7caca33`) из
  [garrytan/gstack](https://github.com/garrytan/gstack), MIT, © 2026 Garry
  Tan. Разбор: `catalog/gstack/items/claims-evidence.md`.

