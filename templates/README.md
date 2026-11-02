# Шаблоны для рабочих репозиториев

| Файл | Куда положить | Задача roadmap |
|---|---|---|
| `CLAUDE.md` | корень рабочего репозитория (или дописать в существующий `CLAUDE.md`) | 0.3 |
| `mcp.json` | корень рабочего репозитория как `.mcp.json` | 1.1 |

## CLAUDE.md: как применять

1. Скопируй `templates/CLAUDE.md` в корень проекта. Если там уже есть
   `CLAUDE.md`, допиши разделы в конец, дубли правил убери.
2. Сверху добавь 3–5 строк о проекте: версия Odoo, команда тестов, линтер.
3. Раздел «Context7» удали, если сервер не подключён (иначе правило
   ссылается на несуществующие инструменты).
4. Закоммить. Правила начинают действовать со следующей сессии.

Размер ~40 строк, около 500 токенов в каждой сессии; не раздувай.

Откуда правила: «пол качества» — `catalog/agent-skills/items/constraint-driven-development.md`;
`shortcut:` и строка «не проверено / риск» — `catalog/ponytail/items/ponytail.md`;
«отсутствие не доказывается поиском» — принцип №28 из
`catalog/one-skill-to-rule-them-all/items/starter-principles.md` (CC BY 4.0,
rebelytics/one-skill-to-rule-them-all); правило Context7 —
`catalog/context7/README.md`.

## Context7: подключение

Нужен ключ. Получает человек на https://context7.com/dashboard (вход через
GitHub/Google), бесплатно 1000 вызовов в месяц. Ключ не вставляй в чат и не
коммить. Перед подключением прочитай политику приватности Context7: в их
сервис уходит текст запросов.

`npx ctx7 setup` не используем: чужой установщик, пишет в `~/.claude*` и шлёт
телеметрию.

### Облачная сессия (claude.ai/code)

1. Открой настройки окружения: меню облачного окружения в заголовке сессии
   → **Edit**.
2. Добавь секрет `CONTEXT7_API_KEY` = ключ: в разделе **Network secrets**
   (в старых версиях приложения **API credentials**), если он есть, иначе
   как переменную окружения. Нужно, чтобы в сессии была переменная
   `CONTEXT7_API_KEY`: `.mcp.json` подставляет её в заголовок.
3. **Network access**: уровень Limited, в **Allowed domains** добавь
   `mcp.context7.com` и `context7.com`; галку «Allow package managers»
   оставь. Подробно: https://code.claude.com/docs/en/cloud-environments#network-access
4. Скопируй `templates/mcp.json` в корень рабочего репозитория как
   `.mcp.json`, закоммить и запушь.
5. Начни **новую** сессию (секреты и сервер подхватываются при старте).
   Проверка: `/mcp` показывает `context7` в статусе connected; запрос
   «Odoo 19: как объявить SQL-ограничение уникальности» должен вызвать
   `query-docs` и вернуть `models.Constraint`.

Если в сессии нет переменной (секрет попал только в сетевой слой), сервер
не подключится с `401`; тогда запиши это в отчёт и попробуй вариант
«переменная окружения».

### Локально

Вариант А, тот же `.mcp.json` (как в облаке):

```bash
export CONTEXT7_API_KEY=ctx7sk-...   # в ~/.zshrc или ~/.bashrc, не в репо
cp templates/mcp.json <рабочий-репо>/.mcp.json
claude   # при первом запуске подтвердить сервер из .mcp.json
```

Вариант Б, только для себя, без файла в репо:

```bash
claude mcp add --transport http --scope user context7 https://mcp.context7.com/mcp \
  --header "Authorization: Bearer $CONTEXT7_API_KEY"
```

Вариант В, без ключа, через OAuth в браузере (только локально):

```bash
claude plugin marketplace add upstash/context7
claude plugin install context7@context7-marketplace
# перезапустить Claude Code, затем /mcp → context7 → вход
```

### На всю организацию

Context7 есть в каталоге коннекторов claude.ai. Подключает администратор
организации; тогда `.mcp.json` не нужен. В нашей организации не проверяли.

### После подключения

Добавь в `CLAUDE.md` проекта раздел «Context7» из шаблона (если удалял).
