# Доказательство установки: install_test.sh + смоук

- **Файлы:** `scripts/install_test.sh`, `smoke_test.py`, `registry_check.py`,
  `xpath_check.py`, `qweb_if_chain_check.py`, `SKILL.md` §5–8 (`@a5507bf`)
- **Лицензия:** MIT
- **Вердикт:** адаптировать методику (пересказ) в `odoo19-mvp-build:testing`/`pr-review`;
  скрипты не ставить без правки `--db`

## Как устроено

`RESULT: CLEAN` ставится, только если выполнены все три условия
(`install_test.sh:73–119`):
1. `odoo-bin -i <modules> --stop-after-init` вернул 0;
2. в логе нет шаблонов `ERROR|CRITICAL`, `Traceback`, `incompatible version`,
   `not installable`, `ParseError`, `ValidationError`, `Element … cannot be located`,
   ошибки сборки бандла, `N failed`, и **нет пропуска браузерных тестов**;
3. `ir_module_module.state = 'installed'` у каждого модуля (через `psql`).

Дальше по `SKILL.md`: `--tests` с демо-данными; сгенерированный смоук-модуль (clickbot по
меню модуля, форма «новый» каждого действия, все страницы website под public и admin;
любая ошибка консоли браузера роняет тест); flow tour главного сценария; повторный
`-u` на той же базе (идемпотентность данных, `noupdate`); `registry_check.py`
(мёртвые `super()`, несуществующие compute по реальному MRO); при сбое — открыть
PNG-скриншоты; в конце хэш исходника, `git status` ядра и отсутствие баз `mig20_*`.

## Что ценно

- **«0 failed» не значит «прошло»**: HttpCase в Odoo пропускается без Chrome или
  `websocket-client`. Поэтому проверяется строка `Open "…" in browser` и сам факт
  пропуска. Это стоит записать в наш `testing`.
- **Повторный `-u`** ловит неидемпотентные данные. В наших чек-листах этого нет.
- **Контрольный прогон**: если сбой похож на проблему ядра, тот же смоук гоняется
  на чистом модуле ядра. Сбой там — не дефект миграции.
- **Никогда не комментировать ради установки**, а записать в «Not migrated».

## Риски

- `--db NAME` + `dropdb --if-exists` в конце: база с любым именем будет удалена.
  Ограничение `mig20_*` есть только в тексте `SKILL.md`.
- Нужны локальные PostgreSQL ≥ 16, Odoo 20 и Chrome. В облаке не запускается.
