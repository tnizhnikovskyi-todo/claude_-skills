# gstack — сводка для главной сессии

**Что это.** garrytan/gstack @ `7caca33` (v1.94.26.0, MIT, 138.8k ★, релизы
2×/нед): 71 скилл «виртуальной команды» (ревью плана, `/review`,
`/investigate`, `/qa` в браузере, `/cso`, `/ship`, дизайн, iOS) + ~300
утилит, свой браузер, хуки, телеметрия, память в `~/.gstack`.

**Вердикт: отклонить установку (10/18), адаптировать 5 методов.**
Против: преамбул ~5.5k токенов на каждый вызов (`/review` ≈ 25–30k),
SessionStart-автообновление чужого кода, код уходит в Codex по умолчанию,
в облаке теряется состояние, `cso` требует Docker.

**Лучшие находки (что взять):**
1. **Gate Integrity** (`review/gate-integrity.md`) → `pr-review`: AC
   переписаны под код, `config['test_enable']` в продуктовом коде,
   ослабленные пороги/assert, «0 тестов = зелёный» (Odoo `--test-tags`).
   Только идея: первоисточник каталога не указан в `NOTICE.md`.
2. **Планка ценности теста** (`test-audit`) → `testing`/`pr-review`:
   карточка `protects/fails_when/why_new/no_claim` («тест под `sudo()` не
   доказывает права»).
3. **Claims Need Evidence + цитата перед находкой** → `templates/CLAUDE.md`,
   `pr-review`, `repo-audit`: вид доказательства; для полей из
   `_inherit`/миксинов цитировать порождающий код.
4. **write-skill** (из skill-diet, MIT) → правила `boost` и
   `weekly-review`: уровни + лестница правки против разбухания скиллов.
5. **investigate + blast radius** (pstack, MIT) → новый
   `boost:debug-root-cause` только после A/B (стоп после 3 гипотез,
   DEBUG REPORT, лестница доказательств).
Плюс идеи: пререгистрация эвалов (`eval-plan`) → `evals/README.md`;
хуки во frontmatter скилла как барьер без always-on.

**Дубли/отклонено:** `office-hours`/`spec`/`plan-*` (есть `interview-me`,
`tr-*`), `context-save`/`learn` (хуже `cloud-memory`), `careful`/`freeze`
(есть права и auto mode), `cso`-рантайм, браузер, дизайн, iOS.

**Открыто:** A/B не делались; разобрать первоисточники skill-diet и
pstack; доступ к приватному маркетплейсу не получен.
