# Пилот codebase-memory-mcp: рабочий журнал

Задача 4.5 `roadmap.md`, ветка `build/cbm-pilot`, 2026-11-02.
Контейнер облачный, эфемерный: 4 CPU, 15 ГБ RAM, x86_64.

## 1. Бинарник: пин и проверка до запуска

- Версия: **v0.12.1** (релиз 2026-10-16, тег → коммит `a7158ac`).
- Артефакт: `codebase-memory-mcp-linux-amd64.tar.gz` с GitHub Releases.
- SHA-256 `8453015145f072c1b9b019cbdd02cea8cc6f18cc5e116036dd20992631c638c7`
  совпал со строкой в `checksums.txt` релиза.
- Подпись Sigstore (`sigstore` 4.5.1 из PyPI в venv scratchpad):
  `sigstore verify github --repository DeusData/codebase-memory-mcp
  --bundle <файл>.bundle <файл>` → `OK` и для архива, и для
  `checksums.txt`. Сертификат: воркфлоу
  `.github/workflows/release.yml@refs/heads/main`, раннер github-hosted.
  Замечание: подписан запуск с `main`, а не с тега (`--ref refs/tags/v0.12.1`
  не проходит); для пина это нормально, но ref тега в сертификате не виден.
- В архиве: бинарник 331 МБ (ELF x86-64, stripped, динамическая линковка
  на glibc), `install.sh` (не запускали), `LICENSE`, `THIRD_PARTY_NOTICES.md`.
- Интересное: у архивов `…-ui-…` и обычных одинаковый SHA-256, то есть UI
  всегда внутри бинарника.

## 2. Запуск заблокирован классификатором auto mode

Две попытки запустить проверенный бинарник (`--help`, затем отдельно
`--version` после повторной сверки SHA-256) отклонены классификатором
auto mode с причиной `[Code from External]`. Обходить блок не стал.
Разрешение из главной сессии («Разрешаю») до классификатора этой сессии не
доходит: нужно правило разрешения в настройках (см. отчёт).

Что сделано без запуска бинарника — ниже.

## 3. Цели подготовлены

- `pilot/` скопирован в scratchpad, отдельный `git init`, коммит `base`.
- `pilot-diff/`: та же копия + незакоммиченный `diff-p4.patch`.
- Odoo 19: `git clone --depth 1 --filter=blob:none --sparse … -b 19.0`,
  `sparse-checkout set addons/{sale,stock,account,product} odoo/addons/base`:
  25 с, 229 МБ без `.git`, 536 `.py`, 386 `.xml`. Код Odoo не запускался.
- `odoo_map.py`: pilot 0,04 с (143 строки карты); odoo19 с
  `--model product.template` 2,0 с (503 строки).

## 4. Статический разбор исходников v0.12.1 (без запуска)

Sparse-клон `src/` и `docs/` тега v0.12.1 в scratchpad.

- **Контекст инструментов:** 17 инструментов, описания + JSON-схемы
  20 449 символов ≈ 5,7k токенов, если клиент грузит их сразу. В Claude
  Code MCP-инструменты обычно откладываются через ToolSearch, тогда
  постоянно в контексте только имена и `instructions` сервера (181 символ,
  ≈ 50 токенов). Самые тяжёлые: `detect_changes` (2,4k симв.),
  `trace_path` (2,0k), `index_repository` (2,0k). Проверить фактическим
  прогоном, когда запуск будет разрешён.
- **Изоляция через окружение:** `CBM_CACHE_DIR` (вместо `~/.cache`),
  `CBM_ALLOWED_ROOT` (какие пути можно индексировать), `XDG_CONFIG_HOME`,
  `CBM_SEMANTIC_ENABLED`, `CBM_LOG_LEVEL`, `CBM_INDEX_SINGLE_THREAD`,
  `CBM_MAX_FILE_BYTES`. Всё это в `run_ab.sh` для плеча MCP.
- **XML:** `.xml` распознаётся как язык (`discover/language.c:328`) и
  попадает в проход `pass_configures` (конфиги). Спец-логики для
  `inherit_id`, `ir.model.access.csv`, `ir.rule` нет; `grep -i odoo` по
  `src/` пуст (как и в разборе каталога).
- **INHERITS:** рёбра наследования строятся из баз классов
  (`pipeline/pass_semantic.c`), то есть из `class X(models.Model)`;
  строковый `_inherit = 'x.y'` таким ребром стать не может. Ожидание
  (не проверено запуском): граф увидит `_inherit` только как строку в
  поиске по коду.

## 5. Вопросы и эталон

`questions.md`: 4 вопроса по пилоту (P1–P4, P4 через `git diff`) и 2 по
ядру (O1–O2), у каждого эталон и «ловушка». Скрипт плеч: `run_ab.sh`.
