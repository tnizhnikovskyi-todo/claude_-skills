# scripts/

## `skill-prescan.py`: префильтр скиллов и плагинов

Детерминированная проверка папки скиллов или плагина **до установки**
(шаг −1 сессии анализа) и **перед публикацией** в маркетплейс. Только
stdlib Python 3.9+, ничего из проверяемого не исполняет, в сеть не ходит.

```bash
# чужой репозиторий, клон в scratchpad
python3 -I scripts/skill-prescan.py "$SCRATCH/ext/<repo>"

# наш плагин перед публикацией (evals/ в маркетплейс не уходит)
python3 -I scripts/skill-prescan.py plugins/boost --exclude evals

# дубли имён и триггеров по всему, что видит сотрудник
python3 -I scripts/skill-prescan.py --roots plugins/boost ../sale_todo_claude/plugins \
    --descriptions account-skills.tsv --exclude evals
```

`account-skills.tsv` — строки `имя<TAB>description` для скиллов, которых
нет на диске (скиллы аккаунта claude.ai, листинг сессии). Имя вида
`plugin:skill` даёт и источник, и имя.

**Выход:** 1 есть BLOCK (с `--fail-on warn` и при WARN), 0 иначе, 2 ошибка
запуска. `--json` для CI, `--verbose` печатает все INFO.

**Уровни:**

| Уровень | Что значит | Что делать |
|---|---|---|
| BLOCK | Грубый признак вредоноса или нарушение нашего правила | Безопасность 0 / не публиковать, пока не разобрано вручную |
| WARN | Опасное возможно, но бывает и законно | Прочитать строку, закрыть как «находка» или «отклонённое подозрение» |
| INFO | Справочно: хуки, MCP, права, хосты, неточные дубли | Сверить с заявленным в README |

**Классы:** `injection` (EN/RU/UK), `remote-exec`, `exfiltration` (секрет +
канал наружу в одном файле), `exfil-channel`, `unresolved-target` (голый
IP, paste/туннели, шортенеры), `dangerous-cmd`, `secret-access`, `hooks`
(события, сеть в хуке = BLOCK), `mcp`, `permissions` (`bypassPermissions`,
широкие `allowed-tools`), `hidden-text` (tag-символы, bidi, zero-width,
HTML-комментарии), `encoded-code` (base64/hex декодируется и сканируется
повторно; «мёртвый» блок помечается), `claim-vs-behavior` («read-only/без
сети» в описании против записи/сети в коде), `install-hook`,
`social-engineering`, `opaque-binary`, `lint`, `broad-trigger`,
`duplicates`, `supply-chain`, `telemetry`.

**Исключение для справок** (урок darwin-skill): в `.md` опасное, которое
только перечислено, понижается: запрет рядом («никогда», «нельзя»,
«never»), кавычки/бэктики со словами «шаблон», «пример», «признак»,
строка таблицы с `\|`, файлы в `references/`, `docs/`, `*checklist*`,
`*patterns*`. В коде — шаблоны внутри регулярок и комментарии. Хуки,
tag-символы, эксфильтрация и «заявление против поведения» не понижаются.

**Граница покрытия.** Это греп: перефразированная инъекция, поток данных
через несколько файлов и семантика («скилл читает почту и отдаёт внешнему
LLM») не видны. Чистый вывод не значит «безопасно»; ручной разбор по
чек-листу безопасности обязателен.

**Тесты:** `python3 -I scripts/tests/skill-prescan/test_prescan.py`
(с `SALE_TODO_DIR=<клон sale_todo_claude>` — ещё и его плагины). Вредные
фикстуры собираются во временной папке из строк теста.

**Атрибуция.** 14 регулярок (помечены `[janitor]` в выводе) взяты дословно
из [khendzel/skills-janitor](https://github.com/khendzel/skills-janitor)
`scripts/security.sh@4b42f39` (строки 93–134), MIT, Copyright (c) 2026
Krzysztof Hendzel; текст лицензии — `tests/skill-prescan/LICENSE-skills-janitor`.
Идеи классов — [berabuddies/Semia](https://github.com/berabuddies/Semia)
@ `379bc25`, Apache-2.0, пересказ. Прототип — `catalog/semia/items/skill_prescan.py`.
