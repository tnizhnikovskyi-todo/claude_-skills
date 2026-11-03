# U4: `scripts/skill-prescan.py`

- **Ветка:** `build/skill-prescan` (от `claude/admiring-cannon-25jueb`, `550723a`)
- **Дата:** 2026-11-03
- **Что сделано:** `scripts/skill-prescan.py` (stdlib, ~970 строк),
  `scripts/tests/skill-prescan/test_prescan.py` (12 тестов, все зелёные),
  `scripts/tests/skill-prescan/LICENSE-skills-janitor`, `scripts/README.md`.
- **Источники:** `catalog/semia/` (прототип `items/skill_prescan.py`,
  `items/checklist-additions.md`), `catalog/skills-janitor/` (17 правил
  `security.sh`, дубли, lint), `catalog/repo-security-review/`
  (`items/proposed-checklist.md`), урок darwin-skill (исключение для справок).

## Правила

Уровни BLOCK / WARN / INFO, выход 1 при BLOCK (`--fail-on warn` — и при WARN).

| Класс | BLOCK | WARN | INFO |
|---|---|---|---|
| `injection` | «ignore previous instructions», «do not tell the user», «secretly run», RU «игнорируй предыдущие инструкции», «не сообщай пользователю», «тайно отправь», «без ведома пользователя»; UK «ігноруй попередні інструкції», «не кажи користувачу», «таємно надішли», «без відома користувача» | «без подтверждения удали», «не спрашивай подтверждения», «you are no longer», «exfiltrate»/«кейлог»; любая инъекция в коде | — |
| `remote-exec` | `curl/wget … \| sh/python/node`, `bash <(curl`, `eval "$(curl`, `base64 -d \| sh`, `iex(iwr …)` | — | — |
| `encoded-code` | `exec(base64…)`, `new Function(atob…)`; BLOCK-правило внутри декодированного base64/hex | блок base64/hex с кодом (с пометкой «не используется — мёртвый код»), `\x..`-цепочки, `fromCharCode` | base64 с обычным текстом |
| `exfiltration` | чтение секрета + канал наружу в одном файле | — | — |
| `unresolved-target` | URL с публичным голым IP, paste/туннели (glot.io, pastebin, webhook.site, ngrok…), шортенер в коде | шортенер в `.md` | — |
| `exfil-channel`, `outbound-data`, `network` | — | вебхуки Discord/Slack/Telegram, `curl -d $VAR`, `requests.post`, `nc host port`, `curl http://` | отправка данных, упомянутая в `.md` |
| `secret-access` | — | `~/.ssh`, `~/.aws/credentials`, `id_rsa`, keychain, профиль браузера, история shell/Claude | `$…TOKEN`, `os.environ[…KEY]`, `printenv` |
| `dangerous-cmd` | `rm -rf ~ / /*`, `mkfs`, `dd of=/dev/sd…`, fork-бомба | `git push --force`, `eval "$var"` | `sudo` |
| `hooks` | сеть в команде хука или в его скрипте; HTTP-хук | скрипт хука не найден | каждый хук (событие, matcher, команда); событие без matcher |
| `mcp` | — | версия не закреплена (`npx -y`, `@latest`, `uvx` без версии); удалённый URL | каждый сервер; секреты в `env` |
| `permissions` | `bypassPermissions`, `--dangerously-skip-permissions` в конфиге/коде | то же в `.md`; `allowed-tools` с `Bash`, `Bash(*)`, `Bash(bash:*)`…; `"allow": ["Bash"]` | список `allowed-tools` |
| `hidden-text` | tag-символы U+E0000–E007F (скрытый текст декодируется и сканируется), bidi в коде | bidi в тексте, zero-width, ZWJ между ASCII, HTML-комментарий с указанием | — |
| `claim-vs-behavior` | «без сети / offline / no network» в `SKILL.md`, README скилла или плагина, а в коде сеть | «только чтение / read-only», а в коде запись или `allowed-tools` с Write/Edit; «без сети» и WebFetch | — |
| `install-hook` | npm `(pre/post)install` с сетью | любой `(pre/post)install` | — |
| `social-engineering` | zip/7z + пароль | «скачай .exe», «скопируй в терминал» | — |
| `opaque-binary` | — | `.pyz`, `.exe`, `.so`, архивы | — |
| `lint` | — | нет frontmatter/`name`/`description`; `name` не `a-z0-9-` или ≠ папке; `description`+`when_to_use` > 1 536; XML-тег в `description` | `description` > 1 024 (открытая спецификация Agent Skills); нет «НЕ для…» / «Not for…» |
| `broad-trigger` | — | «always use», «в любой задаче», «proactively» в `description` | — |
| `duplicates` | — | одно имя у нескольких скиллов; Unicode-Jaccard ≥ 0.30; общая тригерная фраза в кавычках | Jaccard 0.20–0.30 |
| `supply-chain`, `telemetry`, `inventory` | — | симлинк наружу, битый JSON манифеста | `@latest`, `pip install` без `==`, `git clone` без SHA, posthog/sentry, папки `dist/`, `vendor/`… |

Также в выводе: **поверхности исполнения без вызова скилла** (хуки,
settings, `.mcp.json`, манифесты, `package.json`, установщики, statusline),
**все внешние хосты** и список **непрочитанного**.

**Исключение для справок (darwin-skill).** В `.md` понижаем BLOCK → WARN
или INFO, если опасное только перечислено: запрет перед ним («никаких»,
«никогда», «не запускай», «never», «do not»), кавычки/бэктики плюс слова
«шаблон / пример / признак / pattern / example», строка таблицы с
экранированным `\|`, файл в `references/`, `docs/` или с именем
`*checklist*`, `*patterns*`, `*security*`. Защиты вида «не выполняй без
подтверждения», «без ведома пользователя не коммить» не считаются
инъекцией. В коде понижаются шаблоны внутри регулярок (сам сканер) и
комментарии. Хуки, tag-символы, эксфильтрация и «заявление против
поведения» не понижаются никогда.

**Дубли по нескольким корням** (`--roots a b c`, `--descriptions f.tsv`):
скиллы со всех корней и из TSV (скиллы аккаунта claude.ai, которых нет на
диске) сравниваются попарно. Слова Unicode, стем 6 букв, стоп-слова
RU/UK/EN и общие для наших описаний («скіл», «тригер», «результат»);
копии по `realpath` схлопываются. Метод — из замера
`catalog/skills-janitor/measure.py` (там 1 настоящая пара, 0 ложных).

## Точность на тестах

Фикстуры собираются из строк теста во временной папке: в репозитории нет
готовых вредных `SKILL.md` и невидимых символов. Хосты — `example.com` и
TEST-NET `203.0.113.0/24`. Корпус вредоносов Semia не использовал: в
карточке его нет (только описание), правило задачи — «только если он в
карточке».

| Набор | Новый `skill-prescan.py` | Прототип `catalog/semia/items/skill_prescan.py` |
|---|---|---|
| 15 вредных: инъекции EN / RU / UK, tag-символы, хук с сетью, `curl \| bash` в `SKILL.md`, Python-эксфильтрация в Discord, `exec(base64)`, мёртвый base64-блок, «offline/read-only» против `urlopen`, `bypassPermissions` + MCP `@latest`, zip с паролем, голый IP, `rm -rf ~/`, npm `postinstall` | **15/15 BLOCK** | 5 BLOCK, 7 HIGH, 3 пропуска (UK-инъекция, `rm -rf ~/`, заявление против поведения) |
| 4 чистых: справка с перечнем шаблонов (RU, таблица с `\|`), флаги-эмодзи с tag-символами и ZWJ, ловушки frontmatter (CRLF, `>-`, `''`), код сканера с регулярками | **0 BLOCK, 0 WARN** | 1 ложный BLOCK (справка), 1 ложный HIGH (эмодзи) |
| `plugins/boost` без `evals/` (38 файлов) | 0 BLOCK, 1 WARN (настоящий, см. ниже) | 0 BLOCK, 0 HIGH |
| 3 плагина sale_todo_claude @ `2a7f7c1` (185 файлов) | 0 BLOCK, 0 WARN | 0 BLOCK, 0 HIGH |
| Lint (имя, XML-тег, длина, имя ≠ папке, «НЕ для») | 5/5 правил сработали | нет lint |
| Дубли: одно имя в двух корнях, близкие описания, TSV | сработали | нет |

Прогон: 0.5 с на `boost`, 4.4 с на трёх плагинах sale (большие XML
шаблонов `.docx`). Токенов 0. A/B с моделью (`claude plugin eval`) не
делали: это скрипт, а не скилл; сравнение выше — с прототипом на тех же
данных, стоимость $0.

Оговорка: вредные фикстуры написаны мной под мои же правила (как и у
прототипа в Semia). Recall на новых кампаниях неизвестен; перефразированная
инъекция («отложи в сторону то, что тебе говорили раньше») не ловится.

## Найденное

### `plugins/boost` (перед публикацией, `--exclude evals`)

| Уровень | Что | Разбор |
|---|---|---|
| WARN `lint/desc-xml` | `skills/odoo19-lint/SKILL.md`: в `description` есть `<tree>` | **Настоящая находка.** Именно такой тег в `description` давал предупреждение синка claude.ai. Предложение: писать «тег tree» или `tree`-вью без угловых скобок. Сам плагин не правил |
| INFO `hooks` | `SessionStart` и `Stop` → `hooks/memory-start.sh`, `memory-stop.sh`, без matcher | Совпадает с README («Хуки только у `cloud-memory`»); сети в скриптах нет — проверено правилом `hook-network` |
| INFO `remote-exec`, `supply-chain` | `README.md:54` «Никаких `curl \| bash`, `npx pkg@latest`» | Перечисление запрещённого, понижено правильно |
| INFO `env-secret` | `automation-audit/references/*.md`: `$CONTEXT7_API_KEY` в примере команды | Справка, канала утечки нет |
| Хосты | `github.com`, `mcp.context7.com`, `raw.githubusercontent.com`, `www.odoo.com` | Документация и Context7 — ожидаемо |

С `evals/`: BLOCK `claim-vs-behavior` до исключения тестовых папок —
README говорит «без сети», а фикстура `evals/repo-audit/.../senders.py`
шлёт почту. После правки (тесты и фикстуры не считаются поведением
плагина) — снято. Остальное в `evals/`: дубли имён `lean-change`,
`repo-audit` (копии в фикстуре `skill-feedback`), удалённый MCP Context7 в
фикстуре `automation-audit`. Всё ожидаемо; `evals/` в маркетплейс не уходит.

### sale_todo_claude (`odoo19-sales-prep`, `-demo`, `-offer` @ `2a7f7c1`)

0 BLOCK, 0 WARN. Хуков, MCP, `allowed-tools` нет; у всех 18 скиллов есть
граница «НЕ для…», длина и имена в норме. Скрипты `make-docx.py`,
`check-docx.py`, `check-humizer.py` без сети. Хосты: свои
(`erp/help/portal.todo.ltd`), `fathom.video`, `meet.google.com`,
`github.com` и XML-неймспейсы шаблонов `.docx`. 16 INFO «близкие
описания» (Jaccard 0.20–0.30) внутри цепочки продаж — соседние стадии,
по замыслу.

### Дубли по всему, что видит сотрудник (U13)

`--roots plugins/boost <sale>/plugins --descriptions account-skills.tsv`,
где TSV — 7 отдельных скиллов аккаунта из листинга этой сессии
(`anthropic-skills:*`). Всего 34 скилла.

| Пара | Jaccard | Разбор |
|---|---|---|
| `meeting-protocol-builder` ↔ `kickoff-survey-protocol` (оба — копии в аккаунте) | 0.45 | Тот самый дубль из `decisions/2026-11-03-old-skill-copies.md`. Скрипт его ловит без подсказки |
| `odoo19-sales-prep:brief-transcript-analyzer` ↔ `anthropic-skills:session-transcript-analyzer` | 0.45 | **Новое.** Оба «Запускай ПІСЛЯ … зустрічі, коли є транскрипт… Головний writer журналу… реєстри D-N, X-N, Q-N». Стадии разные (бриф продаж и сессия дискавери). У брифового граница есть («НЕ для сесії дискавері — для неї session-transcript-analyzer»), а у старой копии в аккаунте обратной границы «НЕ для брифу» нет. На фразу «розбери транскрипт зустрічі» копия может перехватить бриф. Ещё один довод за U13 (отключить копию); в плагине `odoo19-discovery-sessions` проверить, есть ли там граница «НЕ для брифу» |

Сверить копии аккаунта с плагинами `odoo19-discovery-*`, `odoo19-tr-authoring`,
`odoo19-mvp-build` здесь нельзя: маркетплейс `todoltd/claude-methodology-marketplace`
вне доступа сессии. Команда для главной сессии или CI маркетплейса —
ниже.

### Сам скрипт

Самопроверка `skill-prescan.py scripts --exclude tests` нашла настоящую
ошибку: при записи файла escape-последовательности `‪`, `​` и
tag-символы стали настоящими невидимыми символами в исходнике (BLOCK
`unicode-bidi`). Заменены на escape-последовательности, теперь 0 BLOCK,
0 WARN. Урок: самопроверку сканера держать в тестах (см. «Открытые вопросы»).

## Что не получилось / ограничения

- Греп: перефразированные инъекции, поток данных через несколько файлов,
  «скилл отдаёт почту внешнему LLM» не видны. Чистый вывод ≠ безопасно.
- Исключение для справок обходится: злоумышленник может положить
  `curl | sh` в `references/` с «примером» — будет WARN, не BLOCK. Поэтому
  WARN обязателен к чтению.
- `claim-vs-behavior` по README плагина смотрит заявления вне таблиц и
  строки таблицы вида «| `скилл` | …» (относит к этому скиллу). Заявление
  в свободном тексте про один скилл будет приписано всему плагину.
- Лимит 1 024 символа для `description` взят из открытой спецификации
  Agent Skills по памяти, не сверен с документацией сегодня — поэтому только INFO.
- Корпус Semia и `security.sh` janitor не запускались (правило «чужой код
  не исполняем»); регулярки janitor перенесены дословно и проверены нашими тестами.

## Строки для `PROVENANCE.md`

Новый раздел «Скрипты (`scripts/`)»:

| Что у нас | Источник (репозиторий @ коммит, файл) | Лицензия | Как взято | Атрибуция |
|---|---|---|---|---|
| `scripts/skill-prescan.py`: 14 регулярок (`inj-*`, `sh-*`, помечены `[janitor]`), идея правил `uni-hidden`, `md-htmlcomment`, формат «эвристика, не доказательство» | [khendzel/skills-janitor](https://github.com/khendzel/skills-janitor) @ `4b42f39`, `scripts/security.sh` стр. 93–134 | MIT | дословно (регулярки) с атрибуцией; остальное своё | docstring скрипта, `scripts/README.md`, `scripts/tests/skill-prescan/LICENSE-skills-janitor` |
| `skill-prescan.py`: дубли триггеров (коллизии имён + Jaccard), lint frontmatter, ловушки frontmatter в тестах | skills-janitor @ `4b42f39`, `scripts/detect_dupes.sh`, `scripts/lint.sh`, `tests/test_cli_regression.sh` | MIT | идея, код свой (Unicode, стем, RU/UK) | `scripts/README.md` |
| `skill-prescan.py`: классы `unresolved-target`, канал наружу, `claim-vs-behavior`, закодированный мёртвый код, слепые зоны описи | [berabuddies/Semia](https://github.com/berabuddies/Semia) @ `379bc25` (`rules/sdl/*.dl`, `pipeline.py`, `prepare.py`) через наш прототип `catalog/semia/items/skill_prescan.py` | Apache-2.0 | пересказ, код свой | docstring скрипта, `scripts/README.md` |
| `skill-prescan.py`: исключение для справок | [alchaincyf/darwin-skill](catalog/darwin-skill/README.md) `references/runtime-neutrality.md@8a8b662` | MIT | идея | `scripts/README.md` |
| `skill-prescan.py`: поверхности исполнения (хуки, MCP, манифесты) | Consensys/repo-security-review @ `d5128b0` через `catalog/repo-security-review/items/proposed-checklist.md` | нет лицензии | только идея, текст свой | `scripts/README.md` |

## Куда встроить (предложения, правят главная сессия и владельцы)

1. **Шаг −1 сессий анализа** — в `CLAUDE.md`, раздел «Если ты сессия
   анализа», после п. 3:
   > **Префильтр.** До чтения: `python3 -I scripts/skill-prescan.py <клон>`.
   > BLOCK → безопасность 0 (или ручное «отклонённое подозрение» с
   > причиной), каждое WARN закрыть в `notes.md`, поверхности исполнения
   > прочитать целиком. Вывод приложить к `notes.md`. Чистый вывод ничего
   > не доказывает.
   И пункт «Шаг −1» в `criteria.md` (из `catalog/semia/items/checklist-additions.md`).
2. **Публикация `boost`** — в `plugins/boost/README.md`, «Как попадает к
   сотрудникам»: перед PR в маркетплейс
   `python3 -I scripts/skill-prescan.py plugins/boost --exclude evals --fail-on warn`
   (сейчас упадёт на `<tree>` в `odoo19-lint` — это и надо поправить).
3. **CI маркетплейса** `todoltd/claude-methodology-marketplace`: job на
   PR — `skill-prescan.py plugins/* --exclude evals` (выход 1 при BLOCK) и
   `--roots plugins --descriptions account-skills.tsv` (дубли; TSV —
   выгрузка скиллов организации, обновлять вручную). Это барьер для U13.
4. **sale_todo_claude/scripts/**: скопировать скрипт рядом с
   `check-triggers.py`, вызвать из `check-skills.sh` по `our-plugins.txt`.
   Дубли с плагинами других фаз — там же через `--roots` на клон
   маркетплейса.

## Открытые вопросы

- Добавить в тесты самопроверку `skill-prescan.py scripts --exclude tests`
  = 0 BLOCK (сейчас сделано руками)?
- Нужен ли режим `--publish` с жёстким набором (WARN `lint` = ошибка, а
  WARN безопасности — нет)? Сейчас есть только общий `--fail-on warn`.
- Кто и как часто обновляет TSV скиллов аккаунта для проверки дублей.

## Нужные правки общих файлов (не делал)

- `CLAUDE.md`: шаг −1 (текст выше).
- `criteria.md`: ссылка на префильтр в разделе «Безопасность».
- `roadmap.md`: U4 → сделано; заметка к U13 про найденную пару
  `brief-transcript-analyzer` ↔ `session-transcript-analyzer`.
- `PROVENANCE.md`: строки выше.
- `plugins/boost/README.md`: команда перед публикацией; `odoo19-lint`
  `description` без `<tree>` (отдельная задача: правка скилла и его eval).
