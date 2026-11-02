# Журнал разбора: context7

## 2026-11-02, первичный разбор

**Клон:** `git clone --depth 1 https://github.com/upstash/context7.git` в
scratchpad, коммит `18d6f5d` от 2026-11-02. Код не запускали, `npm install`
не делали.

**Прочитано:**
- `README.md`, `docs/plans-pricing.mdx`
- `.claude-plugin/marketplace.json`, `plugins/claude/context7/*` (плагин =
  один `.mcp.json` на удалённый сервер)
- `packages/mcp/src/index.ts` (регистрация инструментов, инструкции сервера),
  `lib/api.ts` (3 эндпоинта), `lib/encryption.ts` (заголовки),
  `lib/constants.ts` (URL), `lib/research-preview-tools.ts`,
  `lib/telemetry-config.ts`
- `packages/cli/src/utils/tracking.ts`, `setup/agents.ts`,
  `setup/mcp-writer.ts` (что пишет установщик)
- `skills/find-docs/SKILL.md`

**Проверено вживую** (curl к публичному API без ключа, запросы обезличенные):
- `GET /api/v2/libs/search?libraryName=Odoo` → `/websites/odoo` с версиями
  14.0/16.0/17.0/master/19.0, обновлён 2026-10-22; плюс сторонние зеркала.
- `GET /api/v2/context?libraryId=/websites/odoo/19.0&query=computed stored field…`
  → 5,9 КБ, корректно, но `store=True` не раскрыт, дубли на ar/ja.
- то же для SQL constraints → правильный `models.Constraint` (новое в 19),
  ссылки на 19.0 reference; дубли переводов fr/sv/zh_TW.
- `Next.js` → `/vercel/next.js` обновлён 2026-11-01, до v16.2.9.
- Сеть из облачного окружения до `context7.com` открыта.

**Выводы:** см. `README.md`, вердикт «взять» (MCP с ключом + правило).

## Открытые вопросы

1. Политика приватности https://context7.com/privacy: хранят ли запросы,
   используют ли их для обучения или аналитики. Не читали.
2. Коннектор claude.ai (каталог, id `37153cd7-...`): можно ли подключить
   на уровне организации и будет ли он работать в облачных сессиях.
3. Честное A/B-сравнение в Claude Code: одна и та же задача на Odoo 19 с
   Context7 и без него (например, модель с `Constraint`/`Index` и
   `_compute` со `store=True`).
4. Сколько вызовов реально уходит в день при агрессивных инструкциях
   сервера и хватит ли 1000 в месяц на человека.
5. Можно ли через `policies` в дашборде ограничить выдачу официальными
   источниками (отсечь зеркала вроде `/alexmalab/odoo_addons`).

## Вопросы пользователя и решения

(пока нет)
