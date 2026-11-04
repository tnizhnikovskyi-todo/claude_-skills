# Старые копии скиллов в claude.ai дублируют скиллы плагинов

Дата: 2026-11-03. Повод: разбор skills-janitor нашёл одинаковые триггеры
у `meeting-protocol-builder` и `kickoff-survey-protocol`. Задача U13 в `roadmap.md`.

## Что нашли

Кроме плагинов, у аккаунта есть отдельные скиллы (в сессии они видны как
`anthropic-skills:*`). Десять из них загружены в мае–июле 2026 из старых
плагинов (`source: plugin`) и с тех пор не обновлялись. Каждый совпадает
по имени и назначению со скиллом из нынешних плагинов `odoo19-*`. Какой
сработает на общую фразу, не определено. Копии к тому же старее:

| Старая копия (дата) | Строк | Что вместо неё | Строк | Чем копия хуже |
|---|---|---|---|---|
| `kickoff-survey-protocol` (06-03) | 228 | `odoo19-discovery-initiation:meeting-protocol-builder` | 397 | Ранняя версия того же скилла (заголовок внутри — «Meeting Protocol Builder»): калибровка на 41 протоколе против 1013, нет бланка `.docx` в `assets/`, нет границы «НЕ для внутреннего аналізу», нет критик-раунда и правила «термін — доповнюй, не заміняй» |
| `meeting-protocol-builder` (06-12) | 388 | то же | 397 | То же ядро, но без шара плагина (вход из ланцюга дискавері, КБ, критики) и без негативной границы в `description` |
| `sales-handover-analyzer` (05-28) | 177 | `odoo19-discovery-initiation:sales-handover-analyzer` | 337 | Общих строк 26 из 177: старый формат, не знает девʼяти блоків досьє `handover-dossier-builder` |
| `session-transcript-analyzer` (06-12) | 267 | `odoo19-discovery-sessions:session-transcript-analyzer` | 285 | Главный writer журнала дискавери: две версии пишут один журнал по-разному. Префильтр: копия ещё и пересекается с `brief-transcript-analyzer` продаж (у неё нет границы «НЕ для брифу») |
| `security-review` (07-01) | 192 | `odoo19-mvp-build:security-review` | 275 | Без методики Strix; содержит ошибку F3 (`type='json'`) |
| `tr-odoo-tech-design`, `tr-review`, `tr-usecases-acceptance`, `tr-registry-update` (06-01) | 69–120 | `odoo19-tr-authoring:*` | 72–154 | Старые версии цепочки ТР |
| `odoo-spec-writer` (06-11) | 123 | `odoo19-mvp-build:spec-writer` | 123 | Старое имя того же скилла |
| `ite-konsultant` (10-20) | 76 | плагин `ite-konsultant` | 80 | Дубль имени |

Остальные отдельные скиллы (`docx`, `pdf`, `pptx`, `xlsx`, `docs`,
`skill-creator`, `google-workspace`, `import-memory`, `morning`) — от
Anthropic, дублей нет.

## Решение

- На протокол оставить **`odoo19-discovery-initiation:meeting-protocol-builder`**.
  Он новее, он в цепочке (его называют продажи и дискавери, карта
  `siblings_checked`), и он уже универсальный: любой тип зустрічі, не только Odoo.
- `kickoff-survey-protocol` и остальные 9 старых копий **отключить или удалить**
  в claude.ai (настройки → навыки/плагины аккаунта или организации). Сделать
  это может только владелец, из облачной сессии нельзя.
- Перед удалением проверить, что у тех, кто пользовался копиями,
  установлены плагины `odoo19-discovery-initiation`, `odoo19-discovery-sessions`,
  `odoo19-tr-authoring`, `odoo19-mvp-build`, `ite-konsultant`.
- Барьер на будущее: проверка перед публикацией (U4) сверяет имена и
  триггеры всех скиллов, видимых сотруднику, а не только внутри одного плагина.

## Дополнение 2026-11-04: старые плагины в «My Uploads»

Синхронизированный список плагинов аккаунта (локальная копия сессии, 2026-11-04
17:46) показал второй источник с теми же именами — **«My Uploads»**
(`account_uploads`, загружены вручную в июне–июле 2026):

| Плагин | Загружен | Сейчас в маркетплейсе |
|---|---|---|
| `odoo19-mvp-build` | 2026-07-01 | 0.9.4 |
| `odoo19-tr-authoring` | 2026-07-01 | 0.7.1 |
| `odoo19-implementation` | 2026-06-25 | 0.3.0 |
| `odoo19-discovery-initiation` | 2026-06-23 | 0.12.1 |
| `odoo19-discovery-sessions` | 2026-06-23 | 0.7.0 |
| `odoo19-discovery-closeout` | 2026-06-23 | 0.5.0 |
| `todo-install-probe`, `cowork-install-test` | 2026-06 | — (тестовые) |

Те же имена и старые тексты: в сессии одновременно видны, например,
`odoo19-mvp-build` 0.9.4 и 0.8.1. Это тот же класс проблемы, что старые копии
скиллов выше, и, вероятно, их источник. Решение: удалить эти 8 плагинов из
«My Uploads» (claude.ai → настройки → Plugins → My Uploads), оставить
маркетплейс `todoltd/claude-methodology-marketplace`.
