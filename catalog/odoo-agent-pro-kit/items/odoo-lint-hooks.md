# Хуки и линтер (`plugin/hooks/`)

- **Тип:** хуки Claude Code (7 событий) + Python-проверки
- **Источник:** https://github.com/infovpcs/odoo-agent-pro-kit/tree/99515db/plugin/hooks
- **Вердикт:** адаптировать идею линтера; хуки как есть не ставить

## Что делает

`odoo_hook.py` — диспетчер на SessionStart / UserPromptSubmit / PreToolUse /
PostToolUse / Stop / SessionEnd. Вне Odoo-модуля молчит, при ошибке пропускает.

- **`checks/odoo_lint.py`** (221 строка): после каждого Write/Edit файла модуля
  регэкспами ищет версионные ловушки. Правила L1–L18, серьёзность зависит от
  версии (block → exit 2, модель видит ошибку и правит; warn → подсказка).
  Для 19: `<tree>` (L1), `attrs=`/`states=` (L2), `type='json'` в роуте (L3),
  `<group expand=>` в поиске (L4), `res.groups` + `category_id` (L5),
  `_sql_constraints … CHECK` (L6, warn). L7–L17 — Odoo 20. L18 — `license`
  в манифесте и файл LICENSE. Комментарии вырезаются перед поиском. Тип файла
  определяется по пути (`/views/`, `/models/`, `/controllers/`, `/security/`).
- **`checks/guard.py`**: блок `odoo-bin` вне `sandboxctl`, `./manage_modules.sh`
  без `bash`, VCS-записи (`git push/merge/tag/rebase`, `--amend`, `gh pr create/merge`)
  без явного разрешения, разрушительная очистка Docker.
- **`checks/paths.py`**: блок записи Enterprise-кода (`OEEL-1`/`OPL-1`), приватных
  ключей, AWS/Slack/GitHub-токенов, заполненных секретов в `.env`, путей из deny-list.
- **`checks/gates.py`**: `/start-coding` без `docs/tasks.md` и `/testing` без записи
  о тестах блокируются на UserPromptSubmit; Stop-хук один раз не даёт закончить,
  пока в `sessions/<mod>_progress.json` нет результата backend-тестов.

## Какую слабость Claude закрывает

Ровно ту, что мы нашли сами (`synthesis.md`, п. 3): модель пишет конструкции
старых версий Odoo, и модуль не ставится. Линтер — это барьер в духе правила
«второе нарушение лечится барьером», а не новой формулировкой.

## Качество

- Сильное: версионная серьёзность, fail-open, вырезание комментариев, тесты
  (`tests/hooks/test_odoo_lint.py` и др.), объяснение + исправление в каждой находке.
- Ошибки: L3 на 18.0 советует `type='jsonrpc'`, которого в 18.0 нет
  (`18.0/odoo/http.py`, типы `http`/`json`). L6 недооценивает: в 19.0
  `_sql_constraints` игнорируется целиком (`odoo/orm/model_classes.py:162`), а
  линтер только предупреждает и только про `CHECK`.
- Пробелы для нас: нет удалённых полей (`res.partner.mobile`, `title`), нет
  `numbercall`/`doall` в `ir.cron`, нет `users` у `res.groups`, нет `view_mode="tree"`,
  нет `self._context`.
- Регэкспы, не парсер: `L5` ищет `category_id` в 400 символах после `res.groups`.

## Оценка

| Критерий | Балл | Комментарий |
|---|---|---|
| Прирост | 2 | Барьер на ровно нашу слабость; не измерено |
| Частота | 2 | Каждая разработка модуля |
| Надёжность | 1 | Ошибка L3/18, пробелы по полям; guard блокирует наш `git push` |
| Стоимость контекста | 2 | В контекст попадает только вывод; но процесс Python на каждый Bash/Edit |
| Безопасность | 2 | Код прочитан, сети нет, fail-open; блокировки VCS мешают облаку |
| Поддержка | 2 | Активно, с тестами |
| **Итого** | **11/18** | |

## Что взять

Свой `odoo19-lint` (stdlib, ~150 строк) в `boost`: запуск явно скриптом
(`python3 -I lint.py <модуль>`), опционально PostToolUse-хук **только warn**, без
блокировок VCS. Правила: L1, L2, L4, L5 и L3 (только 19), плюс наши — `_sql_constraints`
как block на 19, `res.partner` `mobile`/`title`, `res.groups` `users`, `ir.cron`
`numbercall`/`doall`, `view_mode` с `tree`, `self._context`. Каждое правило со ссылкой на
строку исходника 19.0 (как в `notes.md`). Атрибуция Apache-2.0 при переносе регэкспов.
