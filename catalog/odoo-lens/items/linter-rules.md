# odoo-lens: правила линтера и куда их перенести

Пересказ своими словами по `odoo_lens/features/diagnostics.py` (коммит
`2482f92`). Лицензии у источника нет — формулировки и код не копируем.

Отметки: ✅ сверено с исходниками Odoo (ветки 18.0/19.0), ❔ UNVERIFIED —
взято из кода odoo-lens, перед переносом сверить через `boost:source-check`.

## Правила версий (то, чего не хватает в наших чек-листах)

| Правило | С какой версии | Сверка | Есть у нас? | Куда перенести |
|---|---|---|---|---|
| `_inherit` **списком** без `_name` создаёт новую модель с именем из имени класса (в 18 — расширял) | 19.0 | ✅ | Нет; `odoo-model-map` считает это расширением (ошибка) | `odoo-model-map` (скрипт + SKILL.md + фикстура), `repo-audit`, `pr-review` |
| Для `_inherits` поле-связь Many2one надо объявить явно (`required`, `ondelete='cascade'`), авто-создания больше нет | 19.0 | ✅ | Нет | `repo-audit`, `pr-review` |
| `_sql_constraints` игнорируется → `models.Constraint` | 19.0 | ❔ (упоминается у нас) | Да, `repo-audit` | — |
| `attrs`/`states` во вью удалены → выражения `invisible`/`readonly`/`required` | 17.0 | ❔ | Частично (`attrs`) | добавить `states` (и как параметр поля — тоже игнорируется) |
| `<tree>` → `<list>`; также `view_mode` с `tree`, `tree_view_ref` → `list_view_ref`, **xpath `//tree` в наследнике молча не совпадёт** | 18.0 | ❔ | Частично (`tree`) | `repo-audit`, `pr-review`: xpath и context-ключи |
| Обратное: `<list>` до 18.0 — неизвестный тип вью | <18.0 | ❔ | Нет | только для бэкпортов, низкий приоритет |
| `name_get()` больше не используется → `_compute_display_name` | 17.0 (удалён в 18) | ❔ | Нет | `repo-audit`, `pr-review` |
| `user_has_groups()` удалён → `env.user.has_group(...)` | 18.0 | ❔ | Нет | `repo-audit`, `pr-review` |
| `@api.returns`, `@api.model_create_single` удалены (→ `model_create_multi`) | 19.0 | ❔ | Нет | `repo-audit`, `pr-review` |
| Параметр поля `group_operator` → `aggregator` | 18.0 | ❔ | Нет | `repo-audit` |
| Параметр поля `auto_join` → `bypass_search_access` | 19.0 | ✅ (имя атрибута есть в 19 ORM) | Нет | `repo-audit` |
| Поля `res.groups`/`res.users`: `groups_id`→`group_ids`, `users`→`user_ids`, `category_id`→`privilege_id` | 19.0 | ❔ | Нет | `repo-audit`, `pr-review` (часто в XML данных групп) |
| `__last_update` больше не магическое поле | 17.0 | ❔ | Нет | низкий приоритет |
| `ir.access.csv` вместо `ir.model.access.csv`/`ir.rule` | saas-19.4 | ❔ | Нет | только заметка: к 19.0 не относится |

## Правила связности модуля (не зависят от версии)

| Правило | Есть у нас? | Куда |
|---|---|---|
| Модель/поле/метод/xml-id из модуля, которого нет в `depends` («работает у нас, падает у клиента») | Частично (общий пункт про `depends`) | `pr-review`, `repo-audit`: явная проверка «каждый внешний xml-id/модель → его модуль в `depends`» |
| Ссылка на неизвестное поле в `related`, `@api.depends`, `_order`, `_rec_name`, `currency_field`, `inverse_name` — падение на установке; в `constrains`/`onchange`/`domain` — только лог | Нет (только `compute` без `depends`) | `repo-audit`: градация серьёзности по месту ссылки |
| Кнопка `type="object"` на метод с `_` — Odoo откажет | Нет | `pr-review`, `repo-audit` |
| Кнопка/поле во вью на несуществующий метод/поле | Да (`repo-audit`) | — |
| Python-файл не импортирован в `__init__.py` (в т.ч. закомментированный импорт) | Нет | `repo-audit`, `pr-review` |
| XML/CSV есть в модуле, но не в `data` манифеста (или строка закомментирована) | Частично | `repo-audit`: явно |
| Манифест: модуль в `depends` не существует, файл из `data` не существует | Нет | `pr-review` |
| `env.ref(...)` без `raise_if_not_found=False` на xml-id, которого нет | Нет | `pr-review` |
| «Did you mean» — ближайшее имя при опечатке | — | приём для формата находки |

## Чего у odoo-lens НЕТ (не заменяет наше)

- Безопасность: нет проверок `sudo()`, `cr.execute` с f-строками,
  `auth='public'`/`csrf=False`, моделей без строк в `ir.model.access.csv`,
  `ir.rule`. Это остаётся за `security-review` и `repo-audit`.
- Сверки с SPEC/AC (`pr-review`), архитектурных долгов (`lean-change`),
  производительности (search в цикле).
- Без исходников Odoo на диске проверки «неизвестное поле/метод» молчат
  или помечаются *unverified* — по замыслу автора, чтобы не шуметь.

## Приём, который стоит взять в формат находок

Сообщение линтера — одна строка `файл:строка:кол`, самодостаточная: что не
так, с какой версии, на что заменить. Плюс понижение серьёзности с
пометкой «не проверено: зависимость X не найдена», если источник не виден
целиком. Это близко к нашему `open_proof_gap` из `security-review` и к
блоку «Где не искал» в `odoo-model-map`.
