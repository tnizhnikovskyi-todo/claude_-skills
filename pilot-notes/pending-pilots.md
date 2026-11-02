# Пилоты, которые ждут запуска пользователем

Главная сессия не смогла создать эти чаты: система безопасности не
пропускает запуск чужих программ (rtk, codebase-memory-mcp) без решения
человека. Чтобы запустить: новая облачная сессия на этом репозитории,
режим Auto, первое сообщение — текст ниже. Ветки: `build/rtk-pilot`,
`build/cbm-pilot`.

## 4.4 rtk

Ты сессия реализации в репозитории claude_-skills. Прочитай `CLAUDE.md`
(раздел «Если ты сессия реализации»), `roadmap.md` (задача 4.4), весь
`catalog/rtk/`, `pilot-notes/README.md`. slug `rtk-pilot`, ветка
`build/rtk-pilot`, пути: `pilot-notes/rtk/`, `templates/rtk/`,
`reports/rtk-pilot.md`. Пользователь разрешает запуск rtk в этом
контейнере: OSS-сборка, версия закреплена, SHA-256 сверен до запуска,
`RTK_TELEMETRY_DISABLED=1`, без `rtk init`, хук только через `--settings`
для `claude -p` во временной копии `pilot/`. Измерь на 6–10 задачах с
Bash (git, grep, find, py_compile, `odoo_map.py`) токены, ходы и
правильность с rtk и без; отдельно проверь «тихие потери» важных строк.
Вердикт и, если «взять», setup-скрипт в `templates/rtk/`. Бюджет $5 на
оба плеча. Отчёт `reports/rtk-pilot.md`, коммит и пуш после каждого шага.

## 4.5 codebase-memory-mcp

Ты сессия реализации в репозитории claude_-skills. Прочитай `CLAUDE.md`
(раздел «Если ты сессия реализации»), `roadmap.md` (задача 4.5), весь
`catalog/codebase-memory-mcp/`, `plugins/boost/skills/odoo-model-map/`,
`pilot-notes/README.md`, `pilot-notes/KEYS.md`. slug `cbm-pilot`, ветка
`build/cbm-pilot`, пути: `pilot-notes/codebase-memory-mcp/`,
`templates/codebase-memory-mcp/`, `reports/cbm-pilot.md`. Пользователь
разрешает запуск сервера в этом контейнере: версия закреплена,
контрольная сумма/подпись проверены, без `install` и хуков, подключение
только через `--mcp-config` для `claude -p`. Цели: копия `pilot/` и
sparse-клон 3–5 аддонов Odoo 19 (`sale`, `stock`, `account`, `product`,
`base`), код Odoo не запускать. Замерь время индексации, видит ли граф
строковый `_inherit`/`_inherits`, XML-вью, права (сверь с `KEYS.md` и
`odoo_map.py`), A/B на 4–6 вопросах: MCP vs плагин `boost` vs ничего.
Вердикт и, если «взять», конфиг в `templates/codebase-memory-mcp/`.
Бюджет $6 на все плечи. Отчёт `reports/cbm-pilot.md`, коммит и пуш после
каждого шага.
