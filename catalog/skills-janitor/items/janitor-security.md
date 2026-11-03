# janitor-security

- **Тип:** скилл + скрипт (`skills/janitor-security/SKILL.md`, `scripts/security.sh`)
- **Источник:** https://github.com/khendzel/skills-janitor @ `4b42f39`
- **Лицензия:** MIT
- **Дата разбора:** 2026-11-03
- **Вердикт:** адаптировать (правила → наш линтер перед публикацией)

## Что делает

Обходит каталоги установленных скиллов и регулярками ищет «плохие формы»:
фразы-инъекции в `.md`, скрытый текст, base64, опасные приёмы в скриптах.
Вердикт на скилл: RISK (есть HIGH), REVIEW (есть MEDIUM), PASS. Для каждой
находки — файл и фрагмент. Явно говорит: эвристика, а не доказательство.

## Правила (`scripts/security.sh@4b42f39`, строки 93–134)

| id | Важность | Где | Что ловит |
|---|---|---|---|
| `inj-ignore` | HIGH | md, вне ```` ``` ```` | ignore/disregard/forget previous instructions |
| `inj-conceal` | HIGH | md | do not tell/inform/reveal … the user |
| `inj-secrecy` | HIGH | md | secretly/covertly run/send/…, without the user's knowledge |
| `inj-exfil-word` | MEDIUM | md | exfiltrate, keylog, beacon home |
| `inj-noconfirm` | MEDIUM | md | delete/send/run … without asking/confirmation |
| `inj-newrole` | MEDIUM | md | you are no longer, new/override system prompt |
| `md-htmlcomment` | MEDIUM | md | HTML-комментарий > 20 символов с императивом (curl, upload, ignore…) |
| `md-b64` | MEDIUM | md | base64 ≥ 120 символов, декодируется в > 85% печатных |
| `uni-hidden` | HIGH | все | U+200B, U+2060, U+202A–202E, U+FEFF; ZWJ/ZWNJ только между ASCII (эмодзи не трогает) |
| `sh-curlpipe` | HIGH | скрипты | `curl/wget … \| sh` |
| `sh-b64exec` | HIGH | скрипты | `base64 -d … \| sh`, `echo <blob> \| base64 -d` |
| `sh-creds` | HIGH | скрипты | `~/.ssh/`, `~/.aws/credentials`, `.netrc`, `.gnupg/`, keychain, `gh/hosts.yml` |
| `sh-shortener` | HIGH | скрипты | bit.ly, tinyurl и др. |
| `sh-http` | MEDIUM | скрипты | `curl http://` не на localhost |
| `sh-postout` | MEDIUM | скрипты | `curl -d/-F/-T … $VAR` |
| `sh-eval` | MEDIUM | скрипты | `eval "$…"` |
| `sh-history` | MEDIUM | скрипты | `.bash_history`, `.zsh_history`, `.claude/history.jsonl`, `.claude.json` |

Калибровка: ZWJ в эмодзи, «secretly» в прозе, безобидные HTML-комментарии
не срабатывают; по словам автора, на машине со 178 скиллами — 2 находки.

## Чего не видит (по коду)

1. **Только английский.** Русские и украинские формулировки не ловятся.
2. **Блоки кода исключены** для фраз-инъекций, хотя модель их читает.
3. **Не все невидимые символы:** нет U+E0000–E007F (tag-символы), U+200E/F,
   U+2066–2069.
4. **Не та поверхность для плагина:** сканирует `<plugin>/skills/*`, но не
   `hooks/hooks.json`, `.mcp.json`, `plugin.json`, `agents/`, `commands/`;
   `.json` и файлы без расширения пропускаются. Самое опасное в плагине —
   хуки, которые исполняются без вызова скилла, — вне охвата.
5. **Права не проверяет:** `allowed-tools` (у самого janitor `Bash(bash:*)`),
   `bypassPermissions`, `--dangerously-skip-permissions`.
6. Правило в скрипте срабатывает один раз на файл; остальные места не
   показываются.

## Сравнение с нашим

- `catalog/repo-security-review/items/proposed-checklist.md` — ручной
  чек-лист (что смотреть). janitor даёт автоматизируемую часть (чем
  ловить). Вместе: чек-лист для разбора + линтер-барьер перед публикацией.
- Встроенный `security-review` смотрит дифф кода, а не тексты скиллов.
- `/skill-doctor` и `/doctor` безопасность скиллов не проверяют (docs, 2026-11-03).

## Что берём

Список правил и формат вердикта (PASS/REVIEW/RISK, файл + фрагмент,
«эвристика, не доказательство») — в наш линтер плагинов перед публикацией,
с дополнениями из «Чего не видит». MIT: регулярки можно переносить с
атрибуцией (`Copyright (c) 2026 Krzysztof Hendzel`, MIT, ссылка на
`scripts/security.sh@4b42f39`).
