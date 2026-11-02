# Атрибуція

Метод «питання з гіпотезою» — адаптація скіла `interview-me` з
[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills/tree/main/skills/interview-me)
(версія 0.6.15, коміт `301b02b`), ліцензія MIT, © 2025 Addy Osmani, через нашу версію
`plugins/boost/skills/interview-me` у репозиторії `tnizhnikovskyi-todo/claude_-skills`.

Що взято: гіпотеза з % впевненості; одне питання з догадкою; «одне питання — один «?»»; тест
«можу передбачити відповідь — питання зайве»; переказ з Out of scope; лише явне «так»
(«як вважаєте» — делегування, а не згода); проба «чого б хотіли, якщо не обґрунтовувати».

Що змінено: метод застосовано не до інтерв'ю користувача в чаті, а до підготовки опитувальника для
живої зустрічі з клієнтом: порядок «найризикованіше першим», фільтр анкетних питань за брифом і
журналом, Out of scope зустрічі й кандидати в X-N, переказ, який БА зачитує наприкінці зустрічі.

Текст ліцензії MIT оригіналу:

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
