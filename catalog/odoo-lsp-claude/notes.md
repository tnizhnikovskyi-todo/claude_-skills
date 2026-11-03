# odoo-lsp-claude: рабочий журнал

## 2026-11-03

### Что смотрели

- Клон `softagram/odoo-lsp-claude-code` в scratchpad (вне репо), HEAD
  `721fc31` — единственный коммит (2026-09-28). Прочитаны все 8 файлов
  (311 строк): `LICENSE`, `plugin.json`, `.lsp.json`, `bin/odoo-ls`,
  `scripts/install-odoo-ls.sh`, `templates/odools.toml`,
  `skills/odoo-ls/SKILL.md`, `README.md`.
- Лицензия: `LICENSE` — MIT, «Copyright (c) 2026 Ville Laitila / Softagram
  Oy»; поле `license` в `plugin.json` совпадает. Чужих файлов нет. Сервер
  `odoo-ls` — LGPL-3.0 (`odoo/odoo-ls@release:LICENSE`), отдельно.
- Блобless-клон форка `villelaitila/odoo-ls` + remote апстрима `odoo/odoo-ls`.
  Ветка форка `claude-code-compat` = `09515b2`: один коммит поверх 1.6.0,
  `panic!` → `warn!` + `return` в `register_capabilities`
  (`server/src/core/odoo.rs`).
- **Апстрим:** коммиты автора `df40068` (тот же фикс) и `e142515`
  (регистрировать только то, что клиент поддерживает динамически) входят в
  тег `1.6.1` (`2cca68a`, 2026-10-19), ветки `release` и `alpha`.
  Changelog 1.6.1 прямо упоминает Claude Code. → форк больше не нужен,
  плагин устарел; в 1.6.1 также чинили/ускоряли GoToReference, так что
  «`findReferences` пуст» из SKILL.md, вероятно, устарело (не проверено).
- `odoo-ls@1.6.1`: выгружены только `server/src` и `changelog.md`.
  - `Cargo.toml`: сетевых крейтов нет; git-зависимости ruff 0.15.0,
    oxc crates_v0.127.0, rust-analyzer `lsp-server` 2025-08-04; rust ≥ 1.94.
  - `Command::new`: `python_path -c` (sys.path, версия), `--version`,
    `tsserver` (JS). Телеметрии не нашли (grep `reqwest|hyper|sentry|
    telemetry|TcpStream`).
  - `core/diagnostic_codes_list.rs`: 143 кода; разделы 01 Python, 02 Import,
    03 Odoo (033xx депрекации — всего 3, ни одной про 17–19), 04 Manifest,
    05 XML/CSV, 06 JS. Полезные для «фактов версии»: OLS03002, 03011, 03014,
    03015–03023, 05055–05057, 05073.
  - Версии: ветвления в коде по (15,0)…(20,0), saas 18.1/19.3/19.4.
    Минимальная официальная версия не найдена → UNVERIFIED.
  - CLI: `args.rs` (`--parse`, `-t/--tracked-folders`, `-c/--community-path`,
    `-a/--addons`, `--python`, `-o/--output`, `--config-path`,
    `--selected-config`), `cli_backend.rs` пишет все события `diagnostic` в
    JSON (`{"events": [...]}`).
  - `.github/workflows/Build-release.yml`: бинарники 8 платформ собираются
    по тегу и грузятся как CI-артефакты; готовые бинарники обычно приходят
    в составе расширений (VS Code, PyCharm, Zed, Neovim).
- Маркетплейс `softagram/claude-plugins-marketplace` (`7ae49f2`, 2026-10-30):
  `grep -i odoo` — пусто. Команда `/plugin install odoo-lsp@softagram-plugins`
  из README не сработает.
- В контейнере: `rustc 1.97.0`, `cargo 1.97.0` есть. LSP-инструмента в
  списке инструментов этой сессии нет (LSP-плагинов не включено).

### Что НЕ делали (запрещено заданием)

- Не запускали `install-odoo-ls.sh`, `cargo build`, `odoo_ls_server`,
  обёртку `bin/odoo-ls`.
- Не читали весь Rust-код сервера (2.3 МБ), только грепы и ключевые файлы.

### Решения

- Карточек в `items/` нет: компонент по сути один (плагин-обёртка).
- Вердикт: отклонить плагин; взять идею пакетного `--parse` как
  опционального второго слоя к T2 (только после A/B).

### Открытые вопросы

1. A/B (нужно разрешение на сборку и запуск `odoo-ls` 1.6.1 + клон
   `odoo@19.0`): ловит ли `--parse` `partner_id.mobile`/`title` в коде и
   вью, `_inherit = ['x']` без `_name` (OLS03020?), и сколько это стоит по
   времени/диску в облаке.
2. Появляется ли LSP-инструмент в облачной сессии при включённом
   LSP-плагине (проверить на безопасном официальном LSP, напр. pyright).
3. Минимальная версия Odoo, которую поддерживает `odoo-ls` (вики проекта).
4. Работает ли `findReferences` в 1.6.1 через Claude Code.
