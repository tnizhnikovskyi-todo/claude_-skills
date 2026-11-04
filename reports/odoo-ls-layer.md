# Отчёт: `odoo-ls-layer` — `odoo-ls --parse` как второй слой к `odoo19-lint`

Ветка `build/odoo-ls-layer` (от `claude/admiring-cannon-25jueb`). Основа:
`catalog/odoo-lsp-claude/` (идея «пакетная диагностика `odoo_ls_server
--parse` против исходников 19.0»), `reports/odoo19-lint.md`.

**Статус: ОСТАНОВЛЕНО на шаге 1 (сборка `odoo-ls`).** Решения по второму
слою пока нет: без собранного бинаря сравнение не провести.

## Что сделано

| Шаг | Результат |
|---|---|
| Клон `odoo/odoo-ls` тег `1.6.1` (shallow, с сабмодулем typeshed) в scratchpad | ✅ HEAD = `2cca68aa010e866f5595a390db5b962b0958374c` — совпадает с SHA из разбора `catalog/odoo-lsp-claude/`. 47 МБ |
| Клон `odoo/odoo@19.0` (shallow, single-branch) в scratchpad | ✅ `3cc89565f528accff539a295989891ffba6144fe`, 1.4 ГБ, 37 с. Код Odoo не запускался |
| `cargo build --release` (Rust 1.97 есть в контейнере) | ❌ **заблокировано** классификатором авто-режима сессии: «Code from External». Разрешение владельца пришло системным уведомлением, а не сообщением пользователя в чате, и для классификатора не засчиталось. Блок не обходил |
| Базовые замеры нашего `odoo19_lint.py` (ниже) | ✅ |
| Сравнение, режим `--with-odoo-ls`, A/B | не начаты (зависят от бинаря). Потрачено на A/B: **$0** |

## Базовые замеры `odoo19_lint.py` (сторона «наш линтер» для сравнения)

| Цель | Находки | Время |
|---|---|---|
| `evals/odoo19-lint/tests/bad/td_lint` | 52 ERROR + 10 WARN, 40 правил (по позитиву на каждое правило) | 0.14 с |
| `evals/odoo19-lint/tests/good/td_lint` | 0 | 0.06 с |
| `evals/odoo19-lint/_fixture/addons/td_rental` | 12 ERROR + 2 WARN | 0.06 с |
| Odoo 19.0 `addons/` + `odoo/addons/` (`3cc8956`) — шум | **0 ERROR, 4 WARN**: `read-group` `l10n_dk/models/account_account.py:22` (настоящий) и 3× `toggle-active` в `iot_drivers/server_logger.py:45,122,141` (там не ORM-метод — ложное WARN, новое с прошлой сверки на `e0b25b7`) | 46 с |
| unittest | 14 OK | 0.13 с |
| Установка | 0 зависимостей, stdlib | — |

Попутная находка: 3 ложных WARN `toggle-active` на `iot_drivers` (класс
логгера, а не модель). Не правил: вне задачи; кандидат на правку
`odoo19-lint` (сужать правило до наследников `models.Model`).

## Что нужно, чтобы продолжить

Явное разрешение **в чате этой сессии** (или правило в настройках
разрешений) на:

1. `cargo build --release` в `scratchpad/odoo-ls/server` (запускает
   build-скрипты крейтов, тянет крейты и git-зависимости по сети);
2. запуск собранного `odoo_ls_server --parse` на фикстурах и на исходниках
   Odoo 19.0 (сервер вызывает `python3 -c` для `sys.path`).

После этого план без изменений: сравнение по классам находок (поле/модель
нет в 19.0, не из `depends`, comodel/related/inverse), шум на ядре, время,
размер установки; решение «второй слой / отказ»; при «да» —
`--with-odoo-ls`, кейс A/B, `claude plugin eval --runs 3`, лимит $5.

Важная оговорка к A/B уже сейчас: по `reports/odoo19-lint.md` Bash в eval
закрыт, скилл там работает по таблице, а не скриптом. Режим
`--with-odoo-ls` в `claude plugin eval` не исполнится ни в одном плече,
пока не открыт Bash в песочнице — A/B такого кейса покажет 0 по
построению. Это нужно решить до платного прогона.

## Нужные правки общих файлов

Пока нет. Строка для `PROVENANCE.md` — только если слой будет принят:
`odoo19-lint --with-odoo-ls` ← `odoo/odoo-ls@2cca68a` (1.6.1), LGPL-3.0,
вызывается как внешний бинарь, код не копируется; атрибуция в
`plugins/boost/skills/odoo19-lint/references/attribution.md`.
