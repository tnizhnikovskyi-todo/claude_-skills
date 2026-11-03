# Классы атак и компаньоны → вопросы для Odoo 19

Файлы: `ATTACK-CLASSES.md`, `DATA-ISOLATION-AND-LIFECYCLE.md`,
`WEB-PROTOCOL-AND-AUTH.md` @ `c1c8a8c` (MIT, Cloudflare). Остальные 8
компаньонов (память, клиент, облако, RPC, ресурсы, десктоп, supply chain, AI)
к модулю `td.*` почти не относятся.

## Что внутри

`ATTACK-CLASSES.md`: 9 классов (Injection, Access control, Resource/file,
Crypto/secrets, Business logic, Feature abuse and data leakage, Chained,
Wildcard, Obvious things), у каждого — вопросы, а не сигнатуры. Компаньоны:
`Core discipline` → классы → `Universal moves` → `Validation rules`.
Сквозное правило: «флаг — не находка, проследи последствие».

## Перенос на Odoo 19 (пересказ своими словами + наша адаптация)

Отмечено, есть ли уже у нас в `security-review` (Strix-версия, 6 измерений).

| Их вопрос (источник) | Odoo 19 | У нас |
|---|---|---|
| Есть ли путь к тому же изменению состояния через другую, более слабую проверку? (Access control) | кнопка в форме vs публичный `action_*` по RPC vs контроллер vs cron vs `load()` импорта | частично («публичный метод = RPC») |
| Может ли поле в теле запроса перебить то, что ограничила система прав? (Access control) | `write({'company_id'/'user_id'/'state'/'partner_id': …})` от пользователя без проверки в `write`/`create` | нет |
| Пакетные/экспорт/импорт операции проверяют права на каждый элемент? (Access control, Feature abuse) | `export_data`, `load`, отчёты `ir.actions.report` с `sudo()`, мастер массовых действий | нет |
| Можно ли пропустить шаг машины состояний или повторить завершённый? (Business logic) | вызов `action_confirm`/`action_done` по RPC на записи в «не том» `state`; двойной вызов | нет |
| Поведение при отсутствующей настройке/флаге (Business logic: default and fallback) | `get_param(..., default)` fail-open | есть в T5 (insecure-defaults) |
| Поиск/фильтр/сортировка как оракул (Feature abuse) | `search_count`/`read_group`/домен по полю с `groups=` или по чужим записям под `sudo()` | нет |
| Поле владельца у записи — ещё не изоляция; найти запрос/правило, которое её обеспечивает на каждом чтении и записи (Data isolation: core discipline) | `company_id` без `ir.rule`; правило есть, но `cr.execute`/`sudo()` его обходят («Policy and query disagreement») | есть (измерение 2, 3) |
| Ссылка/токен на объект шире, чем права выдавшего, или живёт после смены прав (Blob and signed-reference overreach) | `access_token` портала, `ir.attachment` по `res_model/res_id`, публичные вложения | нет |
| Мягкое удаление обходится (Soft-delete bypass) | `active=False` + `with_context(active_test=False)` в контроллере/под `sudo()` | нет |
| Производные копии с другими правами (Derived data) | `mail.message`/чаттер, `mail.tracking.value`, логи `_logger` | частично (логи) |
| CSRF: назвать ambient-учётку, изменяющий маршрут, допустимую кросс-сайтовую форму запроса и отсутствующую проверку; маршруты с не-ambient bearer-токеном не подходят (WEB-PROTOCOL rule 4) | `type='http'` POST с `csrf=False`; JSON-роуты на cookie-сессии vs API-ключ | частично (только `csrf=False`) |
| Same-principal / self-impact — не находка (SKILL anti-pattern 5) | внутренний пользователь с нужной группой делает то, что ему положено по SPEC | нет явного правила |
| Defense-in-depth: если слой A предотвращает атаку, отсутствие слоя B — hardening (README) | нет `ir.rule`, но ACL вообще не даёт доступа группе → `SUGGESTION`, не `VULN` | косвенно (уровни) |

`UNVERIFIED` (сверить по `odoo@19.0:odoo/http.py` через `source-check` до
переноса): имя типа JSON-роута в 19.0 (`type='jsonrpc'` при устаревшем
`'json'`), проверяется ли CSRF у JSON-роутов, внешний API `/json/2` с
API-ключом как bearer и как ограничивается scope ключа. Без этой сверки строку
про CSRF/JSON в скилл не писать.

## Куда

`odoo19-mvp-build:security-review` → новый
`references/odoo-attack-questions.md` (12 вопросов выше) + одна строка в
измерения 1, 3, 5 «→ вопросы в `references/odoo-attack-questions.md`».
Это ложится в задачу **T5** `roadmap.md`.

## Оценка

| Критерий | Балл | Комментарий |
|---|---|---|
| Прирост | 2 | 7–8 вопросов, которых нет в нашем чек-листе (поле в теле, пакетные операции, машина состояний, токены/вложения, архив, оракул); A/B не делали |
| Частота | 3 | каждый `security-review` модуля |
| Надёжность | 2 | вопросы, а не правила; зависит от модели |
| Стоимость контекста | 3 | ~60 строк в `references/`, по ссылке |
| Безопасность | 3 | только текст |
| Поддержка | 3 | Cloudflare, активен |
| **Итого** | **16/18** | **Адаптировать** (после сверки Odoo-фактов) |
