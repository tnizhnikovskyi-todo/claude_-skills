# Атрибуция

Скилл `debug-root-cause` — сокращённая адаптация на русском двух
источников под MIT. Код и хуки не переносились, только метод и формат.

1. **gstack `investigate`** —
   [garrytan/gstack](https://github.com/garrytan/gstack) @ `7caca33`,
   `investigate/SKILL.md` (разделы «Iron Law», «How to work», «Report»,
   «Important Rules»), MIT, © 2026 Garry Tan.
   Взято: «без корня не чинить»; стоп после 3 неудачных гипотез с выбором
   «новая гипотеза / эскалация / логирование»; общая посылка двух неудачных
   правок; правка шире 5 файлов → вопрос; веб-поиск только по классу
   ошибки и версии; «перезапуск, таймаут, skip — не гипотеза» (раздел
   «Recipes»); формат DEBUG REPORT и статусы DONE / DONE_WITH_CONCERNS /
   BLOCKED; «never say this should fix it».
   Не взято: преамбула, телеметрия, learnings, хук `freeze`, вопросы
   через AskUserQuestion, рецепты `flake/polluter/race/eval-bisect`
   (сжаты в один абзац), поле `Related`.

2. **pstack `blast-radius`** —
   [cursor/plugins](https://github.com/cursor/plugins) @ `99b609a7`,
   `pstack/skills/blast-radius/SKILL.md`, MIT, © 2026 Lauren Tan.
   Первоисточник раздела `investigate/sections/blast-radius.md` gstack
   (там пересказ, см. `NOTICE.md` gstack). Разобран сам первоисточник.
   Взято: «один факт, из-за которого правка безопасна»; «искать там, где
   grep не видит»; лестница доказательств из 5 ступеней; подтверждённые и
   снятые риски раздельно; «пустой поиск — тоже ответ, вызывающих не
   выдумывать»; `unproven`.
   Не взято: шаг `arena` (несколько моделей), `unslop`, ссылки на `how`/`why`.

Что добавлено нами: Odoo-список «где grep не видит» (`_inherit`, `super()`,
`ir.rule`, `sudo`, данные в базе), запуск тестов Odoo только в тестовой
базе, ступени для корня и фикса (3+ и 4+), правило для сессий без Bash,
поле «Гипотезы» в отчёте. Разбор: `catalog/gstack/items/investigate.md`.

Текст лицензии MIT (одинаков у обоих, меняется строка копирайта):

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
