# rtk — рабочий журнал

## 2026-11-02, первичный разбор

Клон: scratchpad, `develop` @ `22812af6` (2026-11-02). Ничего не собирали и не запускали.
Скачан и проверен (sha256, `tar -t`) архив `rtk-oss-x86_64-unknown-linux-musl.tar.gz`
v1.1.0 — бинарник не запускался.

### Что смотрели

- `Cargo.toml`: workspace `rtk` (Apache-2.0) + `engine` (BUSL-1.1) + `text` + `plugin`;
  `proxy/` отдельно (BUSL-1.1). Фича `engine` по умолчанию; `--no-default-features` = OSS.
- `hooks/claude/rtk-rewrite.sh` (v4): bash+jq, делегирует `rtk rewrite`, протокол кодов
  0 = allow+rewrite, 1 = нет правила, 2 = deny, 3 = rewrite без решения. Чистит
  `RTK_REWRITE_HOST` из env, чтобы унаследованное значение не ослабило гейт.
- `src/hooks/decision.rs`, `permissions.rs`: `AllowRewrite` только при
  `PermissionVerdict::Allow` (явное allow-правило из settings Claude). Default (нет правил)
  → `AskRewrite(Host)` → без `permissionDecision`. Fish-скрипты никогда не auto-allow.
  Для команд с «неаттестуемыми» конструкциями — Defer. Это строже, чем у Headroom
  (там allow по режиму прав) — значит, авто-`allow` в rtk самом по себе не проблема.
- `src/hooks/init/claude.rs`: `rtk init -g` регистрирует `rtk hook claude` в
  `settings.json` (PreToolUse/Bash; PostToolUse только если включён в pipeline), пишет
  `RTK.md` и `@RTK.md` в `CLAUDE.md`, интерактивно спрашивает согласие на телеметрию.
- `hooks/rtk-awareness.md` (453 байта): «Treat it as the complete result» — не берём.
- `src/hooks/session_start.rs`: только для режима прокси (`ANTHROPIC_BASE_URL` на loopback).
- Сеть (`ureq`): `core/telemetry.rs` (compile-time URL + consent + env), `pipeline_remote.rs`
  и `pipeline_cmd.rs` (явные команды `rtk pipeline …`), `classify.rs` (классификатор шлёт
  до 2000 символов вывода во внешний LLM, если пользователь сам настроил upstream и ключ),
  `task_cmd.rs` (явная `rtk task`), `llm_proxy.rs` (localhost).
- `docs/TELEMETRY.md`: opt-in, раз в 23 ч, агрегаты; `RTK_TELEMETRY_DISABLED=1`.
- `src/discover/rules.rs`: ~100 правил. `cat|head|tail` → `rtk read`; `find` → `rtk find`;
  `grep`, `rg`, `ls`, `tree`, `diff`, `curl`, `wget`, `git …`, `gh …`, тест-раннеры,
  линтеры, пакетные менеджеры, `docker`, `kubectl`, `aws`, `psql`.
- `src/cmds/system/read.rs`: уровень по умолчанию `none` — полный текст.
- `src/cmds/git/git_cmd.rs`: `compact_diff` (ханк ≤100 строк, всего 500, ведущий контекст
  ≤3/ханк), отметки `... (N additions truncated)`; `git show <blob>` режется на 8192 байта
  с подсказкой `rtk proxy git show … | tail -n +N`.
- `src/cmds/system/find_cmd.rs:490`: `.hidden(!search_hidden).git_ignore(true)` —
  подтверждает, что `rtk find` прячет скрытое и игнорируемое.
- `install.sh`: берёт последний релиз (или `RTK_VERSION`), проверяет sha256 по
  `checksums.txt` из того же релиза (защита от порчи, не от подмены релиза).
- GitHub (через search API): 85k звёзд, 5.4k форков, 1660 открытых issues, создан
  2026-01-22, ежедневные коммиты. Issues про тихие потери: #3432, #2995 (find/hidden,
  exit codes), #4818 (head/tail), #4749 (pytest E-строки), #1035 (составные команды),
  #4016 (ast-grep), #4676 (relative `CLAUDE_CONFIG_DIR` → теряются deny-правила).
- Релизы: `v1.1.0` (2026-10-25), `v1.0.0` (2026-10-13); Headroom пинит 0.48.0.
  `Cargo.toml` на develop показывает 0.49.0 — release-please держит версию в релизных
  ветках, на develop она не обновляется.

### Решения

- Вердикт «адаптировать (пилот)»: идея и реализация хука хорошие, но фильтры по умолчанию
  слишком агрессивны для `find` и местами для диффов; нужен свой конфиг и A/B.
- Сборка `rtk-oss`: не нужен BUSL-движок.
- Исключить `find`, `cat/head/tail` (у последних выгоды нет, а баги есть).

### Вариант хука без какого-либо allow (если не доверяем `rtk hook claude`)

```bash
#!/usr/bin/env bash
# PreToolUse/Bash: только переписывает команду, решение о правах всегда за Claude Code.
command -v rtk >/dev/null && command -v jq >/dev/null || exit 0
IN=$(cat); CMD=$(jq -r '.tool_input.command // empty' <<<"$IN")
[ -n "$CMD" ] || exit 0
NEW=$(env -u RTK_REWRITE_HOST rtk rewrite "$CMD" 2>/dev/null); RC=$?
case $RC in 0|3) ;; *) exit 0;; esac
[ -n "$NEW" ] && [ "$NEW" != "$CMD" ] || exit 0
jq -c --arg c "$NEW" '.tool_input.command=$c | {hookSpecificOutput:{hookEventName:"PreToolUse",updatedInput:.tool_input}}' <<<"$IN"
```

### Открытые вопросы

1. Разрешит ли пользователь запустить бинарник в этой сессии для A/B (5–10 команд на
   клоне rtk или нашем репо)?
2. Насколько часто Claude Code в облаке вообще зовёт Bash для шумных команд, а не
   `Read`/`Grep`? От этого зависит реальная экономия.
3. Сеть облачного окружения: доступен ли `github.com/.../releases/download` из
   setup-скрипта (из этой сессии — да).
4. Куда класть хук: в каждый рабочий репозиторий или в user settings окружения.
