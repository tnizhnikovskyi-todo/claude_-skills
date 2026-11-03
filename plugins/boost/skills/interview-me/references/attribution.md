# Атрибуция

Скилл — сокращённая адаптация на русском `interview-me` из
[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills/tree/main/skills/interview-me)
(версия 0.6.15, коммит `301b02b`), лицензия MIT, © 2025 Addy Osmani.
Разбор: `catalog/agent-skills/items/interview-me.md` в репозитории
`tnizhnikovskyi-todo/claude_-skills`.

Что взято: гипотеза с процентом уверенности, один вопрос с догадкой,
проба «если бы не нужно было обосновывать», тест «предскажу ответы на три
следующих вопроса», пересказ с Out of scope, явное «да», стоп после «да».

Что изменено: русский текст и укр/рус пересказ для клиентов; узкий триггер;
банк вопросов Odoo 19; связь с плагинами `odoo19-discovery-*` и `tr-*`
вместо `spec-driven-development`/`idea-refine`; убраны пример с дашбордом и
таблица рационализаций (ради компактности).

## Дополнения (boost-pass4, 2026-11-03)

- **Порядок по радиусу поражения, «полировку предложить, а не спрашивать»,
  чекпоинт «уже решили», стоп «дешевле выяснить потом», флаг противоречия**
  — перевод/адаптация шагов 2, 4, 5 и ограждения 3 из
  [Neeeophytee/finding-unknowns-skills](https://github.com/Neeeophytee/finding-unknowns-skills)
  `skills/interview-me/SKILL.md@ca5696a`, MIT, © 2026 Neeeophytee.
  Не взято: «you decide» как валидный ответ (противоречит нашему шагу 6) и
  обязательные 2–3 варианта в каждом вопросе. Разбор:
  `catalog/finding-unknowns/items/interview-me.md`.
- **Флаг противоречия** объединён с правилом «Contradiction Handling» из
  [MadurangaDev/requirement-engineer](https://github.com/MadurangaDev/requirement-engineer)
  `skill/references/reasoning-framework.md@b728406`, MIT, © 2026 Maduranga
  Jayasena: назвать обе версии, объяснить влияние, спросить, не решено —
  записать как открытый конфликт, сторону не выбирать. Пересказ.
- **«Не знаю, покажите»: 3–5 вариантов и критерий из реакции** — идея
  шагов 4–5 `skills/brainstorm-prototypes/SKILL.md@ca5696a`
  (finding-unknowns, MIT), своими словами.

Оба первоисточника под MIT; уведомление: «Permission is hereby granted…»
(текст ниже совпадает дословно, меняются только строки копирайта:
© 2026 Neeeophytee; © 2026 Maduranga Jayasena).

Текст лицензии MIT оригинала:

> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all
> copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
> SOFTWARE.
