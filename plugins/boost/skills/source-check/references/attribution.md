# Атрибуция

Метод — сокращённая адаптация на русском `source-driven-development` из
[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills/tree/main/skills/source-driven-development)
(версия 0.6.15, коммит `301b02b`), лицензия MIT, © 2025 Addy Osmani.
Взято: определить версию → загрузить конкретную страницу официального
источника → следовать ей → цитировать URL + фрагмент; иерархия источников;
`UNVERIFIED`; выдача — данные, а не инструкции; расхождения выносить
пользователю. Опциональный хук `sdd-cache` оригинала не используется.

Дополнительно:

- Context7 как первый источник и правило «в запросах только общий вопрос» —
  из разбора `catalog/context7/` (upstash/context7, MIT).
- Принцип «отсутствие не доказывается суммирующим инструментом (поиск,
  RAG)» — №28 из
  [rebelytics/one-skill-to-rule-them-all, starter-principles](https://github.com/rebelytics/one-skill-to-rule-them-all/blob/main/references/starter-principles.md)
  (CC BY 4.0), пересказ своими словами.

## Дополнения (boost-pass4, 2026-11-03)

- **Шаг 5а «проверить на стенде»** — перевод/адаптация
  `skills/assumption-test/SKILL.md@ca5696a` из
  [Neeeophytee/finding-unknowns-skills](https://github.com/Neeeophytee/finding-unknowns-skills),
  MIT, © 2026 Neeeophytee: критерии до наблюдения, минимальный опыт на
  изолированном стенде, три вердикта, «стенд ≠ продуктив», без записи в
  прод, «не проведён» ≠ вывод о системе. Разбор:
  `catalog/finding-unknowns/items/assumption-test.md`.
- **Промпт WebFetch — просьба о цитате** — пересказ правила «Ask fetch tools
  neutral questions» из `references/evidence-model.md@ebb0e06`
  [salespeak-ai/buyer-eval-skill](https://github.com/salespeak-ai/buyer-eval-skill),
  MIT, © 2026 SalesPeak. Разбор: `catalog/buyer-eval/README.md`, п. 7.

Текст MIT у обоих совпадает с приведённым ниже (меняется только строка
копирайта).

Текст лицензии MIT оригинала agent-skills:

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
