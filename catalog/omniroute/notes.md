# omniroute — рабочий журнал

## 2026-11-02, первичный разбор

**Клон:** `cheaper-inference/OmniRoute`, ветка `main`, `075d6e5` (2026-11-02), в scratchpad
вне репозитория. 3,4 ГБ, 11 992 коммита с 2026-02-18, ~2 366 коммитов за октябрь.
Код не запускали (есть `postinstall`, нативные модули, MITM с sudo).

**Метаданные (GitHub search API):** не форк; ~83,8 тыс. звёзд, ~12,5 тыс. форков, создан
2026-02-13. Раньше жил как `diegosouzapw/OmniRoute` (бейджи в README до сих пор туда).
Автор Diego Rodrigues de Sa e Souza: ~6,1 тыс. из 12 тыс. коммитов. MIT. npm `omniroute`,
Docker Hub, Electron. Родословная: порт идей из `decolua/9router` и CLIProxyAPI.

### Что смотрели

- README (разделы Promise, Combos, Compatible CLIs, Private, MCP, Compression).
- `src/lib/oauth/constants/oauth.ts`, `src/lib/oauth/providers/claude.ts`, список из 28 OAuth-провайдеров.
- `open-sse/executors/claudeIdentity.ts`: имитация claude-cli (UA, Stainless-заголовки, форма тела).
- `open-sse/utils/publicCreds.ts`: XOR-маскировка чужих client_id «от сканеров».
- `src/mitm/` и `src/mitm/targets/*`: перехват `api.anthropic.com`, Copilot, ChatGPT,
  Google Cloud Code (Antigravity), Cursor, Kiro, Zed, Trae, OpenCode; `/etc/hosts` через sudo.
- `docs/security/STEALTH_GUIDE.md` (TLS JA3/JA4 через `wreq-js`, Chrome 124),
  `BAN_DETECTION.md` (детектор банов аккаунтов).
- `open-sse/config/freeModelCatalog.data.ts`: ToS-метки каталога: ok 53, caution 322,
  ambiguous 34, unknown 5, avoid 71 (провайдеры agy, ai21, blackbox, coze, duckduckgo-web,
  fireworks, friendliai, iflytek, kiro, muse-spark-web, nlpcloud, t3-web).
- `src/lib/db/encryption.ts`: AES-256-GCM, но passthrough, если `STORAGE_ENCRYPTION_KEY` пуст
  (в `.env.example` пуст).
- `open-sse/services/compression/types.ts`: сжатие по умолчанию `off`.
- Сеть: телеметрия по умолчанию выключена; внешние хосты проекта `radar.omniroute.online`
  (опциональный каталог), `omniroute.online`.
- `skills/`: 47 `SKILL.md` для управления самим OmniRoute (`omni-*`, `cli-*`) + `ponytail`.

### Выводы

- Догадка «маршрутизация ради экономии» верна, но экономия строится на подписках и
  бесплатных клиентах чужих продуктов с имитацией официальных клиентов. Это не нарушение
  «где-то на краю», а центральная фича (Tier 1 «Subscription» в каскаде).
- Для Claude Code вариантов использования три, все плохие: подменить Claude другой
  моделью; гнать подписку Claude через сторонний прокси (нарушение условий Anthropic,
  риск бана); MITM своего же трафика.
- Безопасность 0 → отклонить. Итог 7/18.

### Пересечения с `freellmapi` (анализ в главной сессии / ветке `analysis/freellmapi`)

Прочитал `catalog/freellmapi/summary.md` из ветки (в чужую папку не писал).

- Та же область: самохостируемый шлюз, сводящий бесплатные тарифы за одним `/v1`,
  роутинг + failover, MCP-сервер, CLI, переписывающий конфиг Claude Code.
- **Разница в масштабе и методах.** freellmapi: ~40 провайдеров, только API-ключи, без
  реверса. OmniRoute: 380 провайдеров, плюс OAuth подписок, имитация клиентов, TLS-stealth,
  MITM, веб-чаты через браузер. OmniRoute строго рискованнее.
- Общие риски: запрос уходит заранее неизвестному провайдеру; free tiers учатся на данных;
  мультиаккаунты/пулы ключей = обход лимитов и риск бана.
- Общая «хорошая идея»: MCP «второе мнение» на одном платном провайдере с ZDR. OmniRoute
  к этому ничего не добавляет, кроме идеи `auto/subscription` (fail closed, без молчаливого
  платного fallback).
- В `skills/` OmniRoute есть `ponytail`; в нашем репо есть ветка `analysis/ponytail`.
  Не проверял, тот ли это проект; стоит сверить главной сессии.

### Открытые вопросы

- Нужно ли глубже разобрать сжатие (RTK/Caveman) как отдельные проекты для экономии
  контекста Claude Code? Это кандидаты в `sources.md`, а не часть OmniRoute.
- Нужен ли разбор MCP-сервера (110 инструментов) — для нас он смысла не имеет без шлюза.
- Запуск в песочнице не делали; без разрешения пользователя не будем.
