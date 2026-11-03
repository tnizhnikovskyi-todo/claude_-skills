# Каталог разобранного

Ведёт главная сессия по итогам слияния веток `analysis/*`.
Общие выводы и план действий: [`../synthesis.md`](../synthesis.md).

Сводка на 2026-11-03 (четыре прохода, 64 репозитория).

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
| codebase-memory-mcp | MCP: граф кода (C, локально) | [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) | **отложить** после пилота: правильность без него уже 28.5/29, строковый `_inherit`/XML не видит | 13/18 | [codebase-memory-mcp](codebase-memory-mcp/README.md) |
| rtk | бинарник + хук: сжатие вывода Bash | [rtk-ai/rtk](https://github.com/rtk-ai/rtk) | **отложить** после пилота: вывод Bash ≈ 2.7% входа, экономия 1–3% | 14/18 | [rtk](rtk/README.md) |
| caveman | скилл стиля + прокси сжатия | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | адаптировать стиль (`cavecrew` 15/18); рантайм отклонить | 11/18 | [caveman](caveman/README.md) |
| serena | MCP: навигация по коду через LSP | [oraios/serena](https://github.com/oraios/serena) | отклонить для Odoo | 9/18 | [serena](serena/README.md) |
| headroom-desktop | десктоп-прокси сжатия токенов | [gglucass/headroom-desktop](https://github.com/gglucass/headroom-desktop) | **отклонить** | 11/18 | [headroom-desktop](headroom-desktop/README.md) |
| freellmapi | шлюз к бесплатным LLM | [tashfeenahmed/freellmapi](https://github.com/tashfeenahmed/freellmapi) | **отклонить** | 10/18 | [freellmapi](freellmapi/README.md) |
| OmniRoute | AI-шлюз с обходом подписок | [cheaper-inference/OmniRoute](https://github.com/cheaper-inference/OmniRoute) | **отклонить** (безопасность 0) | 7/18 | [omniroute](omniroute/README.md) |

¹ Чат оценил по пяти критериям из шести, сумма из 15.

## Третий проход (2026-11-03)

Все 25 — «как есть не ставить»; ценность в идеях. Лицензия указана по факту разбора.

| Что | Тип | Источник | Лицензия | Вердикт | Итог | Карточка |
|---|---|---|---|---|---|---|
| dooservice/odoo-skills | скиллы Odoo 16–20 (5 из `odoo/odoo@20.0:skills/`) | [dooservice/odoo-skills](https://github.com/dooservice/odoo-skills) | LGPL-3 | адаптировать (факты 19.0, правило «одна версия») | 14/18 | [dooservice-odoo-skills](dooservice-odoo-skills/README.md) |
| unclecatvn/agent-skills | справочники Odoo + `odoo_trace.py` | [unclecatvn/agent-skills](https://github.com/unclecatvn/agent-skills) | MIT | адаптировать (API 19.0, Context Brief) | 13/18 | [unclecatvn-skills](unclecatvn-skills/README.md) |
| odoo-lens | LSP + линтер Odoo 16–20 | [ChengyanOo/odoo-lens](https://github.com/ChengyanOo/odoo-lens) | нет | адаптировать идеи (правила устаревшего API) | 12/18 | [odoo-lens](odoo-lens/README.md) |
| modularity | дизайн и ревью модульности (Balanced Coupling) | [vladikk/modularity](https://github.com/vladikk/modularity) | CC BY-NC-SA 4.0 | адаптировать идеи | 12/18 | [modularity](modularity/README.md) |
| follow-up (укр.) | транскрипт → follow-up | [s1vanov/follow-up](https://github.com/s1vanov/follow-up) | CC BY 4.0 | адаптировать (метки спикеров, сомнительные места) | 12/18 | [ukr-follow-up](ukr-follow-up/README.md) |
| kevinlin/skills | gap-analysis, spec-lint и др. | [kevinlin/skills](https://github.com/kevinlin/skills) | MIT | адаптировать выборочно | 12/18 | [kevinlin-skills](kevinlin-skills/README.md) |
| ba-skills | 11 скиллов БА (BABOK) | [uycung/ba-skills](https://github.com/uycung/ba-skills) | MIT | адаптировать (роли, бизнес-кейс) | 11/18 | [ba-skills](ba-skills/README.md) |
| software-estimation-skills | оценка разработки снизу вверх | [Leanware-io/software-estimation-skills](https://github.com/Leanware-io/software-estimation-skills) | MIT | адаптировать узко | 11/18 | [software-estimation-skills](software-estimation-skills/README.md) |
| mastering-technical-sales | конспект книги о пресейле | [tokenaissance/mastering-technical-sales](https://github.com/tokenaissance/mastering-technical-sales) | MIT (обвязка) | адаптировать идеи | 11/18 | [mastering-technical-sales](mastering-technical-sales/README.md) |
| ai-first-estimation | оценка, когда код пишет ИИ | [antondrob/ai-first-estimation](https://github.com/antondrob/ai-first-estimation) | MIT | адаптировать | 11/18 | [ai-first-estimation](ai-first-estimation/README.md) |
| generate-test-book | AC → ручная тест-книга | [Androbito/generate-test-book](https://github.com/Androbito/generate-test-book) | нет | адаптировать идеи (`uat-test-book`) | 11/18 | [generate-test-book](generate-test-book/README.md) |
| LMTY skills | battlecards, win-loss | [LMTYdotcom/skills](https://github.com/LMTYdotcom/skills) | MIT | адаптировать точечно | 10/18 | [lmty-skills](lmty-skills/README.md) |
| erpipe mcp-odoo | MCP Odoo с безопасной записью | [erpipe-org/mcp-odoo](https://github.com/erpipe-org/mcp-odoo) | MIT | адаптировать (механика записи в `odoo-connector`) | 10/18 | [erpipe-mcp-odoo](erpipe-mcp-odoo/README.md) |
| planning-with-files | план и состояние в файлах | [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) | MIT | адаптировать формат (`PLAN.md`) | 10/18 | [planning-with-files](planning-with-files/README.md) |
| SkillOpt | автоулучшение текстов скиллов | [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt) | MIT | идеи адаптировать; инструмент отклонить | 10/18 | [skillopt](skillopt/README.md) |
| presales-agent-skill | пресейл Salesforce | [namit-jpg/presales-agent-skill](https://github.com/namit-jpg/presales-agent-skill) | MIT | адаптировать (граница «нужно от клиента») | 10/18 | [presales-agent-skill](presales-agent-skill/README.md) |
| requirement-engineer | инженер требований | [MadurangaDev/requirement-engineer](https://github.com/MadurangaDev/requirement-engineer) | MIT | адаптировать частично | 10/18 | [requirement-engineer](requirement-engineer/README.md) |
| claude-sow-creation | SOW + MCQ-анкеты | [SB-Celebal/claude-sow-creation](https://github.com/SB-Celebal/claude-sow-creation) | нет | адаптировать узко | 10/18 | [claude-sow-creation](claude-sow-creation/README.md) |
| odoo-agent-pro-kit | платформа разработки Odoo 17–20 | [infovpcs/odoo-agent-pro-kit](https://github.com/infovpcs/odoo-agent-pro-kit) | Apache-2.0 | адаптировать (линтер ловушек 19) | 9/18 | [odoo-agent-pro-kit](odoo-agent-pro-kit/README.md) |
| mart337i odoo-skills | справочники Odoo 17–20 | [mart337i/odoo-skills](https://github.com/mart337i/odoo-skills) | нет | идеи; как источник фактов 19 опасен (9 ошибок из 19) | 9/18 | [mart337i-odoo-skills](mart337i-odoo-skills/README.md) |
| NaCl | 59 скиллов BA → SA → TL | [ITSalt/NaCl](https://github.com/ITSalt/NaCl) | MIT | отклонить; адаптировать 5 методов | 8/18 | [nacl](nacl/README.md) |
| security-harness | мультиагентный аудит безопасности | [dmdhrumilmistry/security-harness](https://github.com/dmdhrumilmistry/security-harness) | MIT | плагин отклонить; методика PR-ревью — адаптировать | 8/18 | [security-harness](security-harness/README.md) |
| opencode-power-pack | сборник 55 скиллов | [waybarrios/opencode-power-pack](https://github.com/waybarrios/opencode-power-pack) | MIT/Apache; часть CC BY-SA | отклонить; 4 идеи | 8/18 | [opencode-power-pack](opencode-power-pack/README.md) |
| repo-security-review | аудит кода и скиллов | [Consensys/repo-security-review](https://github.com/Consensys/repo-security-review) | нет | отклонить; идеи для проверки скиллов | 8/18 | [repo-security-review](repo-security-review/README.md) |
| AI-PreSales-Skills | пресейл по «The PreSales Handbook» | [hangljoe/AI-PreSales-Skills](https://github.com/hangljoe/AI-PreSales-Skills) | MIT (тексты книги — нет) | адаптировать выборочно | 7/18 | [ai-presales-skills](ai-presales-skills/README.md) |

## Четвёртый проход (поиск 2026-11-03)

Все 22 — «как есть не ставить». Лицензия по файлу `LICENSE`, не по поиску.

| Что | Тип | Источник | Лицензия | Вердикт | Итог | Карточка |
|---|---|---|---|---|---|---|
| gstack | 71 скилл «виртуальной команды» + браузер | [garrytan/gstack](https://github.com/garrytan/gstack) | MIT | установку отклонить; 5 методов (Gate Integrity, планка теста, «утверждение — доказательство») | 10/18 | [gstack](gstack/README.md) |
| mcp-server-odoo | MCP Odoo 16–20 (права на стороне модуля Odoo) | [ivnvxd/mcp-server-odoo](https://github.com/ivnvxd/mcp-server-odoo) | MPL-2.0 (модуль Odoo — OPL-1) | адаптировать модель прав «модель × операция» в T3 | 13/18 | [mcp-server-odoo](mcp-server-odoo/README.md) |
| odoo-mcp-19 | MCP Odoo 19 через JSON-2 | [AlanOgic/odoo-mcp-19](https://github.com/AlanOgic/odoo-mcp-19) | MIT | адаптировать (блок-лист моделей, x2many; нашёл дыры в T3) | 12/18 | [odoo-mcp-19](odoo-mcp-19/README.md) |
| odoo-functional-agent | требование → конфигурация Odoo 20 на демо | [xmglord/odoo-functional-agent](https://github.com/xmglord/odoo-functional-agent) | MIT | адаптировать (маркер стенда, правила одобрения) | 9/18 | [odoo-functional-agent](odoo-functional-agent/README.md) |
| odoo-migrate-to-20 | миграция 14–19 → 20 | [tanim913/odoo-migrate-to-20](https://github.com/tanim913/odoo-migrate-to-20) | MIT | адаптировать (0 ошибок в фактах, 13 в версиях; правила для T2) | 11/18 | [odoo-migrate-to-20](odoo-migrate-to-20/README.md) |
| odoo-lsp-claude | обёртка над `odoo-ls` | [softagram/odoo-lsp-claude-code](https://github.com/softagram/odoo-lsp-claude-code) | MIT (`odoo-ls` — LGPL-3) | отклонить; идея `odoo-ls --parse` вторым слоем к T2 | 9/18 | [odoo-lsp-claude](odoo-lsp-claude/README.md) |
| panus-odoo-dev-skill | скилл Odoo 16–19 + сканер | [panusbodee-owen/odoo-dev-skill](https://github.com/panusbodee-owen/odoo-dev-skill) | нет | отклонить; 3 правила в T2 (идеи) | 9/18 | [panus-odoo-dev-skill](panus-odoo-dev-skill/README.md) |
| odoo-spec-kit | кит стандартов Odoo (OpenSpec) | [focuz-ai/odoo-spec-kit](https://github.com/focuz-ai/odoo-spec-kit) | MIT, внутри чужое | **отклонить** (14 из 17 утверждений неверны для 19) | 5/18 | [odoo-spec-kit](odoo-spec-kit/README.md) |
| caliper | A/B агента со скиллами/MCP и без | [edonadei/caliper](https://github.com/edonadei/caliper) | MIT | методику адаптировать, CLI не ставить | 13/18 | [caliper](caliper/README.md) |
| upskill | генерация и оценка скиллов | [huggingface/upskill](https://github.com/huggingface/upskill) | Apache-2.0 | идеи адаптировать (leave-one-out, правило принятия) | 10/18 | [upskill](upskill/README.md) |
| darwin-skill | эволюция скилла с откатом | [alchaincyf/darwin-skill](https://github.com/alchaincyf/darwin-skill) | MIT | идеи (парное A/B, лимит роста текста) | 8/18 | [darwin-skill](darwin-skill/README.md) |
| skills-janitor | цена контекста, дубли, скан инъекций | [khendzel/skills-janitor](https://github.com/khendzel/skills-janitor) | MIT | адаптировать (линтер плагинов перед публикацией) | 8/18 | [skills-janitor](skills-janitor/README.md) |
| semia | статический аудит скиллов | [berabuddies/Semia](https://github.com/berabuddies/Semia) | Apache-2.0 | инструмент отклонить; идеи + наш префильтр 16/18 | 9/18 | [semia](semia/README.md) |
| cloudflare-security-audit | многофазный аудит безопасности | [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | MIT | скилл отклонить; 12 вопросов и барьер покрытия → T5 | 10/18 | [cloudflare-security-audit](cloudflare-security-audit/README.md) |
| claude-smart | поправки → правила (always-on) | [ReflexioAI/claude-smart](https://github.com/ReflexioAI/claude-smart) | Apache-2.0 | плагин отклонить; промпты извлечения → `skill-feedback` | 9/18 | [claude-smart](claude-smart/README.md) |
| ecc | сборник 314 скиллов, 28 хуков | [affaan-m/ECC](https://github.com/affaan-m/ECC) | MIT; часть CC BY-SA / Apache | установку отклонить (≈33k токенов always-on); 6 вставок | 7/18 | [ecc](ecc/README.md) |
| finding-unknowns | поиск неизвестного (рамка 2×2) | [Neeeophytee/finding-unknowns-skills](https://github.com/Neeeophytee/finding-unknowns-skills) | MIT | адаптировать (`blindspot-pass`, «вкус показывают») | 12/18 | [finding-unknowns](finding-unknowns/README.md) |
| awesome-qa-skills | 169 QA-скиллов | [naodeng/awesome-qa-skills](https://github.com/naodeng/awesome-qa-skills) | **PolyForm Noncommercial** | только идеи (статусы UAT, матрица AC → кейсы) → T11 | 12/18 | [awesome-qa-skills](awesome-qa-skills/README.md) |
| claude-sdlc-skills | SDLC: аудит требований, гейт | [TsCarpe/claude-sdlc-skills](https://github.com/TsCarpe/claude-sdlc-skills) | MIT | адаптировать частично (блок «Повнота» в `tr-review`) | 11/18 | [claude-sdlc-skills](claude-sdlc-skills/README.md) |
| buyer-eval | оценка поставщика глазами покупателя | [salespeak-ai/buyer-eval-skill](https://github.com/salespeak-ai/buyer-eval-skill) | MIT | точечно (измерения закупки); не запускать — шлёт данные вендору | 8/18 | [buyer-eval](buyer-eval/README.md) |
| humanizer-uk | редактура украинского от ИИ-следов | [panchlab/humanizer-uk](https://github.com/panchlab/humanizer-uk) | MIT | адаптировать в `check-humizer.py` | 11/18 | [humanizer-uk](humanizer-uk/README.md) |
| anti-ai-slop-writing | письмо en/ru/uk + детектор | [git-voitenko/anti-ai-slop-writing](https://github.com/git-voitenko/anti-ai-slop-writing) | MIT | адаптировать (бот-хвосты, кальки) | 11/18 | [anti-ai-slop-writing](anti-ai-slop-writing/README.md) |
