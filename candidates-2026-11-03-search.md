# Кандидаты: поиск 2026-11-03 (вместо `/find-skills`)

Поиск: GitHub `search/repositories`, 14 запросов (Odoo / ERP / пресейл / БА /
качество и безопасность скиллов / память), активность после 2026-08-01.
Найдено 173 новых репозитория, уже разобранные 45 отфильтрованы.
Ниже шортлист по пользе для нас. Лицензии взяты из поиска GitHub, и
им нельзя верить без проверки: в третьем проходе 4 из 25 оказались другими.
Сверять по файлу `LICENSE`.

## A. Odoo (связь с F1/T2/T3, коннектор, линтер)

| # | Репозиторий | ★ | Лицензия (поиск) | Зачем смотреть |
|---|---|---|---|---|
| A1 | [ivnvxd/mcp-server-odoo](https://github.com/ivnvxd/mcp-server-odoo) | 411 | MPL-2.0 | Самый популярный MCP для Odoo; модель прав и безопасность записи против нашего `odoo-connector` (F1, T3) |
| A2 | [AlanOgic/odoo-mcp-19](https://github.com/AlanOgic/odoo-mcp-19) | 11 | MIT | Odoo 19 и JSON-2 API (`/json/2`) — новый способ доступа, которого у коннектора нет |
| A3 | [xmglord/odoo-functional-agent](https://github.com/xmglord/odoo-functional-agent) | 0 | MIT | Требование → конфигурация Odoo на демо-базе с ревью и тестом; сверить с `config-spec`/`demo-base-builder` |
| A4 | [tanim913/odoo-migrate-to-20](https://github.com/tanim913/odoo-migrate-to-20) | 13 | MIT | Миграция 14–19 → 20 «с доказательством установки»; задел на 20.0 |
| A5 | [softagram/odoo-lsp-claude-code](https://github.com/softagram/odoo-lsp-claude-code) | 0 | MIT | Плагин официального `odoo-ls`; сравнить с odoo-lens и T2 |
| A6 | [panusbodee-owen/odoo-dev-skill](https://github.com/panusbodee-owen/odoo-dev-skill) | 2 | нет | Поиск устаревшего кода 16–19; только идеи, сверить правила с T2 |
| A7 | [focuz-ai/odoo-spec-kit](https://github.com/focuz-ai/odoo-spec-kit) | 2 | MIT | Стандарты и линтеры Odoo для ИИ |

## B. Качество и проверка скиллов (наш цикл A/B и ревью)

| # | Репозиторий | ★ | Лицензия (поиск) | Зачем смотреть |
|---|---|---|---|---|
| B1 | [edonadei/caliper](https://github.com/edonadei/caliper) | 229 | MIT | A/B реального агента с скиллами/MCP и без — ровно наш метод; сравнить с `claude plugin eval` |
| B2 | [huggingface/upskill](https://github.com/huggingface/upskill) | 761 | Apache-2.0 | Генерация и оценка скиллов |
| B3 | [alchaincyf/darwin-skill](https://github.com/alchaincyf/darwin-skill) | 6781 | MIT | Оценка → правка → тест → откат; сравнить с SkillOpt и `skill-feedback` |
| B4 | [khendzel/skills-janitor](https://github.com/khendzel/skills-janitor) | 125 | MIT | Что съедает контекст + скан prompt injection в скиллах |
| B5 | [berabuddies/Semia](https://github.com/berabuddies/Semia) | 615 | Apache-2.0 | Аудит безопасности скиллов до установки |
| B6 | [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | 57980 | MIT | Многофазный аудит с независимо проверенными находками; против `security-review` |
| B7 | [ReflexioAI/claude-smart](https://github.com/ReflexioAI/claude-smart) | 791 | Apache-2.0 | Поправки пользователя → предпочтения и скиллы; против `skill-feedback`/`cloud-memory` |
| B8 | [affaan-m/ECC](https://github.com/affaan-m/ECC) | 296302 | MIT | Самый популярный сборник (скиллы, память, безопасность); проверить, что из него реально работает |

## C. БА, пресейл, QA, украинский текст

| # | Репозиторий | ★ | Лицензия (поиск) | Зачем смотреть |
|---|---|---|---|---|
| C1 | [Neeeophytee/finding-unknowns-skills](https://github.com/Neeeophytee/finding-unknowns-skills) | 361 | MIT | Поиск неизвестного и уточнение требований; против `interview-me` и вопросов дискавери |
| C2 | [naodeng/awesome-qa-skills](https://github.com/naodeng/awesome-qa-skills) | 295 | NOASSERTION | QA от требований до релиза; для T11 `uat-test-book` |
| C3 | [TsCarpe/claude-sdlc-skills](https://github.com/TsCarpe/claude-sdlc-skills) | 65 | MIT | Приём и аудит требований, враждебный гейт ревью |
| C4 | [salespeak-ai/buyer-eval-skill](https://github.com/salespeak-ai/buyer-eval-skill) | 69 | MIT | Как покупатель оценивает поставщика — взгляд клиента для `defence-brief` |
| C5 | [panchlab/humanizer-uk](https://github.com/panchlab/humanizer-uk) | 1 | MIT | Редактура украинского текста от ИИ-оборотов; против нашего Humizer |
| C6 | [git-voitenko/anti-ai-slop-writing](https://github.com/git-voitenko/anti-ai-slop-writing) | 0 | MIT | То же + детектор без зависимостей (EN/RU/UK) |

## Не берём в шортлист

Академические, медиа, маркетинг, крипто, Kafka/KiCad/Rust, чужие ERP
(SAP, Sage, 1С, Frappe, Kingdee), рабочие места и десктоп-оболочки,
AGPL-шлюзы (anythingmcp, odoo-claude-mcp, clawsec): к нашим задачам не
относятся или лицензия мешает взять даже код примеров.
Полный список 173: `scratchpad/new.tsv` этой сессии (не в git).
