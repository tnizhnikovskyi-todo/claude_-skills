# Аддоны, которые ставит Headroom

Headroom сам по себе — витрина отобранных инструментов экономии контекста.
Список полезен как список кандидатов для нас. Код аддонов не читали.

| Аддон | Что это | Тип | Для нас |
|---|---|---|---|
| [context7](https://github.com/upstash/context7) | Актуальная документация библиотек по версиям | MCP (`mcp.context7.com/mcp`) | **Кандидат №1**: в `inventory/current.md` прямо отмечено, что MCP для документации библиотек нет |
| [serena](https://github.com/oraios/serena) | Символьная навигация по коду (читать функцию, а не файл) | MCP | Кандидат для больших кодовых баз (Odoo-модули) |
| [codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) | Граф знаний по кодовой базе, постоянный | MCP | Кандидат для памяти/контекста |
| [markitdown](https://github.com/microsoft/markitdown) | PDF/Office → Markdown перед чтением | CLI + хук | Частично перекрыт скиллами `pdf`, `docx`, `xlsx`, `pptx` |
| [caveman](https://github.com/JuliusBrussee/caveman) | Сжатые ответы, меньше выходных токенов | плагин | Сомнительно: страдает читаемость ответов пользователю |
| [ponytail](https://github.com/DietrichGebert/ponytail) | Подталкивает к более простому коду | плагин | Перекрыт `simplify` |
| [chisle](https://github.com/JayPokale/Chisle) | caveman + ponytail + обрезка длинного вывода | плагин | Сомнительно |

Интересно: в собственном `.serena/` и `.claude/settings.json` репозитория
видно, что автор сам работает с serena и `rtk grep`.
