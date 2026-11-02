# OmniRoute: подписочный OAuth, stealth, MITM

- **Тип:** часть шлюза (провайдеры-исполнители, `src/lib/oauth`, `src/mitm`, `open-sse/services/*TlsClient`)
- **Источник:** https://github.com/cheaper-inference/OmniRoute
- **Версия / коммит:** 3.8.53, `075d6e5`
- **Дата разбора:** 2026-11-02
- **Вердикт:** **отклонить категорически**

## Что делает

Даёт шлюзу доступ к моделям не по API-ключу, а через **потребительские подписки и
бесплатные клиенты** других продуктов. Для этого OmniRoute проходит OAuth от имени чужого
приложения, затем выдаёт себя за это приложение на каждом запросе. Где провайдер ловит
неофициальных клиентов, включается имитация TLS-отпечатка Chrome и «правильного» порядка
заголовков. Для IDE, которые нельзя перенастроить, есть MITM: корневой сертификат +
`/etc/hosts`, чтобы перехватить их трафик к официальному API.

## Как устроен (что прочитано)

| Файл | Что там |
|---|---|
| `src/lib/oauth/constants/oauth.ts` | 28 OAuth-конфигов: Claude (`claude.ai/oauth/authorize`, scope `user:sessions:claude_code`), Codex, Antigravity, Grok, Kimi, Qoder, Kiro, Cursor, Copilot… |
| `open-sse/utils/publicCreds.ts` | Чужие client_id/secret хранятся XOR-маской «чтобы не срабатывали сканеры» |
| `src/lib/oauth/providers/claude.ts` | Обмен кода, вызов `api.anthropic.com/api/claude_cli/bootstrap` с `User-Agent: claude-cli/<ver> (external, cli)`, импорт токенов из локального Claude Code |
| `open-sse/executors/claudeIdentity.ts` | Подделка заголовков Stainless SDK, версии CLI, формы тела запроса «как у настоящего claude-cli» |
| `docs/security/STEALTH_GUIDE.md` | TLS JA3/JA4 через `wreq-js` (Chrome 124 macOS), модули `claudeCodeFingerprint`, `claudeCodeObfuscation`, TLS-клиенты для Perplexity, Grok, Notion, LMArena |
| `src/mitm/targets/*` | Перехват `api.anthropic.com` (Claude Code), `api.githubcopilot.com`, `chatgpt.com`, `cloudcode-pa.googleapis.com` (Antigravity), Cursor, Kiro, Zed, Trae, OpenCode |
| `src/mitm/sudoGate.ts`, `childExitCleanup.ts` | Правка `/etc/hosts` с sudo, пароль кешируется на сессию |
| `open-sse/services/browserBackedChat.ts` | Веб-чаты (DuckDuckGo, T3 и др.) через headless-браузер |
| `docs/security/BAN_DETECTION.md` | Автоопределение забаненных аккаунтов по тексту ошибок |

## Оценка

| Критерий | Балл | Комментарий |
|---|---|---|
| Прирост | 0 | Для нас ноль: у нас легальный доступ к Claude |
| Частота | 0 | |
| Надёжность | 0 | Ломается при каждом обновлении официального клиента; авторы сами держат «pinned captured release» |
| Стоимость контекста | — | |
| Безопасность | **0** | Нарушение условий провайдеров, риск бана рабочих аккаунтов, MITM с корневым CA, sudo |
| Поддержка | 3 | Активно чинится, именно поэтому так много коммитов |

## Риски и заметки

- Документация говорит, что stealth «не для обхода ToS», но сами механизмы (подмена клиента,
  TLS-отпечаток, обфускация client_id, детектор банов, пулы аккаунтов с «fair-share») ровно
  для этого и нужны.
- Для Anthropic: использование OAuth-токена подписки Claude Pro/Max/Team вне Claude Code не
  разрешено; токен компании, пропущенный через чужой прокси, ещё и попадает в SQLite
  стороннего приложения.
- Отдельно: функция «team sharing one subscription → key pools» прямо противоречит
  лицензиям потребительских подписок.
