# general: общий набор задач (roadmap 0.2, 0.5)

Показывает влияние плагина целиком. Два уровня:

- **регрессионный** (все кейсы): базовая модель проходит их на 0.9–1.0;
  скилл не должен ухудшать результат;
- **`hard`** (тег): кейсы, где базовая модель без плагина стабильно
  ошибается (0.74–0.77). Прирост от скиллов искать здесь.

```bash
# весь набор (кейсам с записью файлов нужен Write/Edit)
claude plugin eval plugins/boost --case 'general/*' --runs 3 --allow-tools Write Edit --max-cost-usd 5 --no-publish -j 4
# только трудный уровень
claude plugin eval plugins/boost --tag hard --runs 3 --allow-tools Write Edit --no-publish -j 4
```

Без `--allow-tools Write Edit` кейсы `odoo19-port`, `odoo19-api-traps`,
`odoo19-sales-traps` проваливаются из-за окружения (файлы не записаны).

| Кейс | Что проверяет | Грейдеры | Для скиллов |
|---|---|---|---|
| `odoo19-constraint` | Устаревший API: `_sql_constraints` → `models.Constraint` | regex ×2, llm | 1.1, 1.3 |
| `vague-task` | Уточнить расплывчатую задачу до работы | llm (trace), regex «нет кода модели» | 1.2 |
| `tr-requirements` | ТР: граница 10%, повторное согласование, отказ, несколько строк | regex GWT, llm | 1.2, 3.3 |
| `discovery-questions` | Найти противоречие FIFO/FEFO в заметках, ≤7 конкретных вопросов | llm ×2 | 3.4 |
| `pr-review-bug` | Найти compute без присваивания в ветке `else`, без ложных блокеров | llm ×2 | 2.2, 3.2 |
| `fact-check` | 3 утверждения (одно ложное), у каждого вердикта источник | llm ×2 | 1.3, 2.2 |
| `bug-hunt` | Округление долей рассрочки: причина + фикс с распределением остатка | llm | 2.2 |
| `keep-it-simple` | Простое поле без переусложнения в коде и непрошеных предложений | llm ×2, regex ×2 | 2.3 |
| `odoo19-port` | Порт модуля 16 → 19, шесть ловушек API, результат в файлах | regex ×11, llm | 1.1, 1.3 |
| `self-check-history` | `history_file`: своя ошибка на единицу и ложные «проверил» в прошлых ходах | llm ×2 | 2.2 |
| `self-check-long` | `history_file`: факт «праздники строками» в середине разговора, «учтено» без правки кода | llm ×2 | 2.2 |
| `pr-review-multi` | Большой PR, 4 ошибки разного рода (утечка через sudo, TypeError в кроне, поиск по нехранимому полю, неполный depends) | llm ×4 | 2.2, 3.1, 3.2 |
| `long-spec-conflicts` | ТЗ ~150 строк, просят оценку, внутри 3 противоречия | llm ×4 | 1.2, 3.3 |
| `reconcile-payments` | 60 счетов и 60 оплат, 5 расхождений и приманка | llm ×2, regex ×5 | 2.2 |
| **`odoo19-api-traps`** `hard` | Группы, крон, группировка, архив, телефон водителя: API, изменённый в 18–19 | regex ×8, llm; вес 5 у ошибок, ломающих установку | 1.1, 1.3 |
| **`odoo19-sales-traps`** `hard` | UoM, товар, строки заказа, обращение и мобильный клиента в 19 | regex ×11, llm; вес 5 у ошибок установки | 1.1, 1.3 |

Заметки:
- Факты Odoo 19 в грейдерах сверены с исходниками ветки `19.0`
  (`odoo/odoo`): удалены `res.partner.mobile`, `res.partner.title`,
  `res.groups.users/category_id`, `res.users.groups_id`, `ir.cron.numbercall`,
  `sale.order.line.product_uom`, `uom.uom.category_id`; устарели `read_group`,
  `toggle_active`, `_notify_progress`, `self._cr/_context/_uid`.
- Регулярки на код пропускают строки-комментарии (`^(?![ \t]*#)`, флаг `m`):
  модель часто пишет «# поле mobile удалено в 19».
- `_tools/mkhist.py` собирает минимальный транскрипт для `history_file` из
  `history.json`; `_tools/mk_reconcile.py` генерирует данные сверки.
- Кейс с `history_file` идёт в одном плече (без Δ): CLI считает, что история
  переносит плагин в оба плеча. Baseline для него — прогон копии плагина без
  `skills/`.
- Имя кейса задано как `general/<папка>` во frontmatter, иначе
  `--case 'general/*'` их не находит.
- `AskUserQuestion` в headless-прогоне агенту недоступен (нет в списке
  инструментов), поэтому вопросы проверяются по тексту ответа.
- Результаты прогонов и разбор в `reports/foundation.md`.
