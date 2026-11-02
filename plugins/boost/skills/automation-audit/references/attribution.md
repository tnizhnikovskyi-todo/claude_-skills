# Атрибуция

Скилл `automation-audit` адаптирован из скилла `claude-automation-recommender`
плагина **claude-code-setup** (Anthropic,
https://github.com/anthropics/claude-plugins-official/tree/a7ba5b93db0c7c8d17f3f1d25853adca79598a1a/plugins/claude-code-setup,
версия 1.0.0, коммит `a7ba5b9`, лицензия Apache License 2.0). Разбор:
`catalog/claude-code-setup/` репозитория claude_-skills.

Что взято (в пересказе и переводе, не дословно): трёхфазная схема
«профиль → рекомендации по категориям → отчёт», правило «1–2 рекомендации
на категорию, 3–5 если спросили про одну», режим только чтения, скелет
таблиц «признак → хук/MCP/скилл/субагент».

Что изменено: добавлены Python/Odoo 19 и облачные сессии (эфемерный
контейнер, setup-скрипт, `SessionStart`, секреты окружения); обязательная
сверка с уже установленным (`known-setup.md`, `.claude/`, `.mcp.json`,
`CLAUDE.md`, шаблоны); у каждой рекомендации поля «Подтверждено» и «Цена»;
раздел «Не рекомендую»; запрет дорогих always-on хуков и общих субагентов
(выводы `synthesis.md`); убраны веб-поиск, macOS-уведомления и неполные
команды (`claude mcp add context7`, `--mcp-debug`).

Изменения в соответствии с п. 4(b) Apache 2.0 отмечены здесь.
