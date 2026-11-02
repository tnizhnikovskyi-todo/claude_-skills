# FreeLLMAPI: ядро-шлюз (`server/`)

- **Тип:** самохостируемый HTTP-прокси-роутер LLM
- **Источник:** https://github.com/tashfeenahmed/freellmapi/tree/main/server
- **Версия / коммит:** `21d287ae`
- **Дата разбора:** 2026-11-02
- **Вердикт:** отклонить для работы с рабочими/клиентскими данными

## Что делает

Принимает запросы в форматах OpenAI (`/v1/chat/completions`, `/v1/responses`,
`/v1/embeddings`, медиа), Anthropic (`/v1/messages`), Gemini (`/v1beta`), Ollama;
выбирает модель из «цепочки» (fallback chain) по скорингу скорости, надёжности и
«интеллекта», расшифровывает ключ провайдера в памяти, проксирует запрос, при
429/5xx ставит ключ на кулдаун и пробует следующую модель. Заголовок
`X-Routed-Via` показывает, кто ответил.

## Как устроен

- Express 5 + SQLite, ~45 платформ в `shared/types.ts`; 10 с отдельными
  адаптерами, остальные через `providers/openai-compat.ts`.
- Базовые URL провайдеров захардкожены; удалённый каталог задаёт только модели,
  лимиты, «квирки» и включённость для уже известных платформ (`hasProvider`).
- Каталог: `GET https://api.freellmapi.co/v1/latest` раз в 12 ч, проверка
  подписи Ed25519 по закреплённому ключу. Отключить нельзя напрямую, но можно
  перенаправить `CATALOG_BASE_URL` / `CATALOG_PUBKEY`.
- Логирование: таблица `requests` хранит метаданные (модель, токены, задержка,
  IP и User-Agent клиента), без текста промптов. Текст сохраняется в кэше
  ответов (если включён) и в беседах Playground.
- Доп. сервисы: сжатие промптов, Fusion (несколько моделей + арбитр), передача
  контекста при смене модели, веб-поиск (Brave, Tavily, Exa, Firecrawl…), Fetch
  Relay / SOCKS / прокси на каждый ключ.

## Провайдеры (по коду и `docs/en/providers/01-supported-platforms.md`)

**Официальные first-party free tiers:** Google Gemini, Groq, Cerebras, Mistral,
Cohere, Cloudflare Workers AI, NVIDIA NIM, Hugging Face Router, Ollama Cloud,
OVHcloud (анонимно), SEA-LION, Reka, SiliconFlow, AMD Radeon Cloud.

**Агрегаторы:** OpenRouter (`:free`), Requesty, Kilo Gateway (анонимно, промпты
логируются для обучения), LLM7, BazaarLink, AnyAPI, OrcaRouter, UnoRouter,
NaraRouter (требует Telegram-верификацию), xKiro, Routeway (требует
браузерный User-Agent для обхода Cloudflare).

**Китай:** Zhipu/Z.ai, ModelScope (Alibaba, нужна верификация личности КНР),
Baidu Qianfan, Volcengine (ByteDance), iFlytek Spark, LongCat (Meituan).

**Малоизвестные шлюзы с «бесплатными» проприетарными моделями:** api.airforce,
ElectronHub, Experiential Labs (отдают Claude-маршруты), Lucidity, DreamPrompting,
Waterfall, Logfare, apinex.bond, aiapi-pro, kiosapi.id, kenari.id, router9,
septorlabs, navy, plugsky, speka, onomeo, clod, blockrun, gizmo, nabh.cloud и др.
Модели по ним приходят в основном из закрытого платного каталога. Сам проект
признаёт, что проверяет только эхо `model id` в ответе — «не независимая
проверка весов». Откуда у этих шлюзов бесплатный доступ к GPT/Claude/Grok —
неизвестно; это типичный профиль перепродажи чужих ключей/триалов.

**Волонтёрские:** AI Horde (запрос исполняет анонимная машина волонтёра).

## Оценка

| Критерий | Балл (0–3) | Комментарий |
|---|---|---|
| Прирост | 1 | Доступ к моделям слабее Claude, без гарантий |
| Частота | 1 | Редко применимо к нашим задачам |
| Надёжность | 1 | Free tiers без SLA, плавающее качество |
| Стоимость контекста | 3 | Вне контекста Claude |
| Безопасность | 1 | Код аккуратный, но поток данных к неизвестному заранее третьему лицу |
| Поддержка | 3 | Очень активен |
| **Итого** | **10/18** | |

## Риски и заметки

См. `../notes.md`, раздел «Риски».
