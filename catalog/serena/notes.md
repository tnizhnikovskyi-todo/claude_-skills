# serena: рабочий журнал

## 2026-11-02, первичный разбор

**Источник.** Клон `https://github.com/oraios/serena` в scratchpad
(`.../scratchpad/ext/serena`), коммит `ede329a` (2026-10-28). Это тот же
репозиторий, что упомянут в `catalog/headroom-desktop/items/addons.md`.
Код не запускали, ничего не устанавливали.

**Что смотрели:**
- `README.md`, `LICENSE`, `LICENSES/`, `pyproject.toml`.
- `docs/01-about/070_privacy.md`, `docs/02-usage/070_security.md`,
  `030_clients.md` (раздел Claude Code), `045_memories.md`,
  `050_configuration.md` (trusted projects), `docs/04-evaluation/*`.
- `src/serena/agent.py` (`_send_usage_info`), `analytics.py`,
  `dashboard/dashboard_api.py` (PyPI-проверка, news), `hooks.py`,
  `mcp.py` (instructions), `tools/*.py`, `constants.py`,
  `resources/serena_config.template.yml`, `resources/config/contexts/claude-code.yml`,
  `modes/editing.yml`, `prompt_templates/system_prompt.yml`.
- `src/solidlsp/ls_config.py`, `language_servers/pyright_server.py`.

**Проверки:**
- Сеть: `grep https://` по `src/serena`. Найдено: `oraios-software.de/serena_usage.php`
  (телеметрия при старте, opt-out `SERENA_USAGE_REPORTING=false`),
  `oraios-software.de/serena_news.json` и `pypi.org` (дашборд), `dot.net`
  (установка .NET для C#-серверов). Других обращений нет.
- Активность: 406 коммитов с 2026-08-01; основные авторы Dominik Jain,
  Michael Panchenko (Oraios). Первый коммит 2025-03-23. Теги v2.0.0
  (2026-10-13), v2.1.0 (2026-10-19).
- Лицензия: SolidLSP — MIT, приложение — GPL-3.0-or-later с v2; до v1.7.0
  (тег `mit-final`) MIT. Нужен CLA для вкладов.
- Odoo/XML: `grep -i odoo` по репо — ноль совпадений. XML-сервера в
  `src/solidlsp/language_servers/` нет. Python по умолчанию — pyright через
  `uvx` (`LanguageServerDependencyProviderUvx`).
- Хук `remind`: пороги 3 Grep / 3 Read / 4 смешанных подряд → deny с
  напоминанием, не чаще раза в 120 с. Состояние в pickle.
- Размер описаний инструментов: статический разбор AST (без импорта кода).
  Скрипт `scratchpad/scripts/tooltok.py`: берёт docstring класса и `apply`,
  +~60 символов на параметр. Включено в `claude-code`+LSP: 22.5k символов
  (≈5.6k ток.), всего с JetBrains/опциональными: 53.9k (≈13.5k ток.).
  Оценка грубая (схемы параметров считаются приблизительно).

**Наблюдения:**
- Документация признаёт: «описания встроенных инструментов CC ~16k токенов…
  почти невозможно убедить Opus 4.7 использовать Serena». Поэтому хуки-запреты
  и подмена системного промпта. Это тревожный сигнал по надёжности
  триггера и по вмешательству в поведение.
- Режим `editing` говорит агенту не перепроверять результат `rename_symbol`.
  Для Odoo это прямой путь к пропущенным ссылкам в `_inherit`-классах и XML.
- Оценка авторов — самооценка агентом; CC-отчёт сделан с JetBrains-бэкендом.

## Открытые вопросы

1. Живое испытание на модуле Odoo 19 (нужно «да» пользователя: установка
   `serena-agent` и pyright из PyPI в контейнер, запуск LS).
2. Сколько реально экономит `get_symbols_overview` + `find_symbol` против
   `Read` с offset на файле ~2000 строк.
3. Видит ли graphify `_inherit` строкой (открыто и в его карточке) — если
   нет, то стоит ли делать свой скрипт «карта моделей Odoo».
4. Какую команду установки serena использует аддон в headroom-desktop
   (README serena предупреждает про устаревшие команды в маркетплейсах).
