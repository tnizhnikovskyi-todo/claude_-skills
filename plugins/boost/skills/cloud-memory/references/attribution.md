# Источники идей

Код из внешних репозиториев **не копировался**: скилл и хуки написаны с нуля.
Взяты только идеи, по разборам в этом репозитории.

| Идея | Источник | Лицензия | Разбор |
|---|---|---|---|
| Индекс на старте вместо полного содержимого; поиск в три шага (индекс → отбор → полные записи); типы наблюдений `decision`/`bugfix`/`discovery`; тег `<private>`; `handoff`-файл для следующей сессии | claude-mem, https://github.com/thedotmack/claude-mem (v15.8.3) | Apache-2.0 | `catalog/claude-mem/` |
| Наблюдения как файлы с YAML-frontmatter и статусами (`open/…/superseded`); git как хранилище памяти | one-skill-to-rule-them-all (task-observer 3.8.1) | CC BY 4.0 | `catalog/one-skill-to-rule-them-all/` |
| «Отсутствие не доказывается поиском» (starter-principle №28) | там же | CC BY 4.0 | `catalog/one-skill-to-rule-them-all/items/starter-principles.md` |
| Фильтр «стоит ли записывать» (трение или неочевидный путь ≥ 3 действий; без петель инфраструктурных ошибок); формат «путь успеха» (Применимо / Делать / Ограничения / Избегать / Проверка) для `bugfix`/`discovery`; долговечное правило только по «всегда / на будущее»; текст инструментов ≠ слова пользователя | ReflexioAI/reflexio @ `49659eb` (движок claude-smart 0.3.17), `reflexio/server/prompt/prompt_bank/playbook_should_generate/v3.0.0.prompt.md`, `playbook_extraction_context/v4.6.1.prompt.md` | Apache-2.0 | пересказ своими словами, изменено (сокращено, переведено, поля под наш формат) | `catalog/claude-smart/` |
| `memory/PLAN.md`: цель, «следующий шаг», шаги со статусом, таблица ошибок с попытками, «3 неудачи → к пользователю», внешний текст не в подмешиваемые файлы, 5 вопросов полноты handoff. Наше: чекбокс `[x]` только после выполненной проверки, проверка у каждого шага, файл коммитится | OthmanAdi/planning-with-files @ `0fa6c79`, `templates/task_plan.md`, `skills/planning-with-files/SKILL.md` (© Ahmad Othman Ammar Adi), https://github.com/OthmanAdi/planning-with-files | MIT | пересказ своими словами, структура упрощена | `catalog/planning-with-files/` |
| Память о структуре проекта (тип `discovery` для фактов «где что лежит») | graphify, Graphify Labs | Apache-2.0 | `catalog/graphify/` |

Отличия от claude-mem: нет фонового воркера, базы, модели-наблюдателя,
MCP и сети; ничего не пишется автоматически; запись делает Claude по
правилам скилла, хранится в git проекта и видна в ревью.
