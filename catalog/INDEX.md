# Каталог разобранного

Ведёт главная сессия по итогам слияния веток `analysis/*`.
Общие выводы и план действий: [`../synthesis.md`](../synthesis.md).

Сводка на 2026-11-02 (два прохода, 17 репозиториев).

| Что | Тип | Источник | Вердикт | Итог | Карточка |
|---|---|---|---|---|---|
| Context7 | удалённый MCP (документация библиотек) | [upstash/context7](https://github.com/upstash/context7) | **взять** | 14/18 | [context7](context7/README.md) |
| Firecrawl | облачный API + MCP (веб-скрейпинг) | [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) | адаптировать (hosted MCP точечно) | 14/18 | [firecrawl](firecrawl/README.md) |
| ponytail | плагин: скиллы + хуки (против overengineering) | [dietrichgebert/ponytail](https://github.com/dietrichgebert/ponytail) | адаптировать (тексты скиллов) | 14/15¹ | [ponytail](ponytail/README.md) |
| agent-skills | плагин: 24 скилла инженерного процесса | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | адаптировать выборочно | 13/18 | [agent-skills](agent-skills/README.md) |
| Strix | CLI AI-пентестер + методология | [usestrix/strix](https://github.com/usestrix/strix) | методология: адаптировать; CLI: отложить | 15/18 и 12/18 | [strix](strix/README.md) |
| graphify | CLI + скилл (граф знаний кода) | [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) | адаптировать (CLI по требованию) | 11/18 | [graphify](graphify/README.md) |
| claude-mem | плагин: хуки + воркер (память) | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | адаптировать идею; cloud-вариант отклонить | 11/18 | [claude-mem](claude-mem/README.md) |
| claude-code-setup | официальный плагин (аудит автоматизаций) | [маркетплейс](https://claude.com/marketplace/plugins/claude-code-setup) | адаптировать | 11/18 | [claude-code-setup](claude-code-setup/README.md) |
| arena-skill | скилл: турнир субагентов | [Jakeschincariol/arena-skill](https://github.com/Jakeschincariol/arena-skill) | адаптировать («арена-лайт») | 10/18 | [arena-skill](arena-skill/README.md) |
| one-skill-to-rule-them-all | мета-скилл самоулучшения скиллов | [rebelytics/one-skill-to-rule-them-all](https://github.com/rebelytics/one-skill-to-rule-them-all) | адаптировать | 10/18 | [one-skill-to-rule-them-all](one-skill-to-rule-them-all/README.md) |
| codebase-memory-mcp | MCP: граф кода (C, локально) | [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) | адаптировать (сервер с пином, без хуков) | 13/18 | [codebase-memory-mcp](codebase-memory-mcp/README.md) |
| rtk | бинарник + хук: сжатие вывода Bash | [rtk-ai/rtk](https://github.com/rtk-ai/rtk) | адаптировать (пилот) | 14/18 | [rtk](rtk/README.md) |
| caveman | скилл стиля + прокси сжатия | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | адаптировать стиль (`cavecrew` 15/18); рантайм отклонить | 11/18 | [caveman](caveman/README.md) |
| serena | MCP: навигация по коду через LSP | [oraios/serena](https://github.com/oraios/serena) | отклонить для Odoo | 9/18 | [serena](serena/README.md) |
| headroom-desktop | десктоп-прокси сжатия токенов | [gglucass/headroom-desktop](https://github.com/gglucass/headroom-desktop) | **отклонить** | 11/18 | [headroom-desktop](headroom-desktop/README.md) |
| freellmapi | шлюз к бесплатным LLM | [tashfeenahmed/freellmapi](https://github.com/tashfeenahmed/freellmapi) | **отклонить** | 10/18 | [freellmapi](freellmapi/README.md) |
| OmniRoute | AI-шлюз с обходом подписок | [cheaper-inference/OmniRoute](https://github.com/cheaper-inference/OmniRoute) | **отклонить** (безопасность 0) | 7/18 | [omniroute](omniroute/README.md) |

¹ Чат оценил по пяти критериям из шести, сумма из 15.
