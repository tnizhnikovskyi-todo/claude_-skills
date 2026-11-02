# Источники идей

Код из внешних репозиториев **не копировался**: скилл и хуки написаны с нуля.
Взяты только идеи, по разборам в этом репозитории.

| Идея | Источник | Лицензия | Разбор |
|---|---|---|---|
| Индекс на старте вместо полного содержимого; поиск в три шага (индекс → отбор → полные записи); типы наблюдений `decision`/`bugfix`/`discovery`; тег `<private>`; `handoff`-файл для следующей сессии | claude-mem, https://github.com/thedotmack/claude-mem (v15.8.3) | Apache-2.0 | `catalog/claude-mem/` |
| Наблюдения как файлы с YAML-frontmatter и статусами (`open/…/superseded`); git как хранилище памяти | one-skill-to-rule-them-all (task-observer 3.8.1) | CC BY 4.0 | `catalog/one-skill-to-rule-them-all/` |
| «Отсутствие не доказывается поиском» (starter-principle №28) | там же | CC BY 4.0 | `catalog/one-skill-to-rule-them-all/items/starter-principles.md` |
| Память о структуре проекта (тип `discovery` для фактов «где что лежит») | graphify, Graphify Labs | Apache-2.0 | `catalog/graphify/` |

Отличия от claude-mem: нет фонового воркера, базы, модели-наблюдателя,
MCP и сети; ничего не пишется автоматически; запись делает Claude по
правилам скилла, хранится в git проекта и видна в ревью.
