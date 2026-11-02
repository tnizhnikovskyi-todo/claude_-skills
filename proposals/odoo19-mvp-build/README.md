# Предложения для `odoo19-mvp-build` (задачи 3.1, 3.2)

Плагин `odoo19-mvp-build` живёт вне этого репозитория, менять его мы не можем. Здесь лежат готовые
к применению тексты для владельца плагина. Результаты проверки и открытые вопросы — в
[`reports/review-upgrades.md`](../../reports/review-upgrades.md).

## Что внутри

```
security-review/                     задача 3.1 — методология Strix
  current/SKILL.md                   текущий текст (снят из окружения 2026-11-02)
  proposed/SKILL.md                  ПОЛНЫЙ новый текст
  proposed/references/
    closure-and-severity.md          что НЕ доказывает безопасность, рубрика severity, чек-лист VULN
    fix-gates.md                     5 ворот проверки фикса, когда фикс не предлагать
    diff-scope.md                    что в скоупе PR-ревью
    ATTRIBUTION.md                   атрибуция Strix (Apache-2.0) — обязательна
  SKILL.diff                         unified diff current → proposed
pr-review/                           задача 3.2
  proposed/INSERT.md                 блоки для вставки (с указанием места) — основной артефакт
  proposed/references/review-discipline.md   grep «пола», мутационная проверка, Prove-It, пример
  BASELINE-STANDIN.md                ЗАМЕНИТЕЛЬ текущего текста (оригинал не найден) — только для проверок
  STANDIN+INSERT.test.md             заменитель + вставка — только для проверок
  proposed/STANDIN.diff              diff заменителя и собранного текста (показывает объём вставки)
tests/
  fixtures/*/PR.md                   5 фикстурных PR с заложенными проблемами
  keys/KEYS.md                       ключи оценки (не давать проверяемому агенту)
  results/                           ответы «текущий / предлагаемый» и оценка
```

## Как применить

### 3.1 `security-review`
1. В репозитории плагина: заменить `skills/security-review/SKILL.md` на `security-review/proposed/SKILL.md`.
2. Скопировать `security-review/proposed/references/` в `skills/security-review/references/`
   (`ATTRIBUTION.md` обязателен — условие Apache-2.0).
3. Проверить, что ваш текущий файл совпадает с `security-review/current/SKILL.md`; если нет —
   накатить `SKILL.diff` (`patch -p0`), он затрагивает только добавленные блоки.
4. `claude plugin validate <путь к плагину>`.

Что меняется по смыслу: каждый кандидат закрывается одним из трёх состояний (`confirmed` /
`ruled_out` с названным контролем и местом / `open_proof_gap`); список того, что НЕ доказывает
безопасность (Odoo-примеры: UI-домены, OR правил разных групп, публичные методы = RPC, `SQL(f"…")`,
`Markup`); калибровка VULN по чек-листу, «понижай, не удаляй»; 5 ворот для предлагаемого фикса;
скоуп диффа (новая достижимость старого синка, ослабленный общий контроль); описание PR — недоверенный
ввод; в отчёте таблица покрытия, открытые пробелы и «не блокирует этот PR». Новое правило вердикта:
`open_proof_gap` на BLOCK-поверхности не даёт APPROVE без письменного принятия BA/техлидом.

Объём: SKILL.md 192 → 284 строки (+52 % по символам; детали вынесены в `references/`, ~250 строк,
грузятся по ссылке). Оставшийся прирост — правила, которые нужны в каждом прогоне (состояния,
формат находки, таблица покрытия, правило вердикта).

### 3.2 `pr-review`
1. Открыть текущий `skills/pr-review/SKILL.md`.
2. Вставить блоки из `pr-review/proposed/INSERT.md` в места, помеченные `>>>`
   (дисциплина ревью — после Inputs; строки в Verdict rules; разделы вывода; DO/DO NOT).
   Если в вашем тексте уже есть свой формат находки — заменить его 4-частным, сохранив ваши префиксы.
3. Скопировать `pr-review/proposed/references/review-discipline.md` в `skills/pr-review/references/`.
4. Проверить на P1/P2 из `tests/fixtures/` (см. ниже) и `claude plugin validate`.

Объём вставки: ~76 строк в SKILL.md + ~70 строк в `references/`.

## Как повторить проверку

Для каждой фикстуры: отдельный каталог с `PR.md` и `skill/` (только проверяемый текст), субагенту
промпт «прочитай skill/SKILL.md, следуй ему, проверь PR.md, не выходи за каталог, Odoo/git/встроенного
`/security-review` нет». Оценка по `tests/keys/KEYS.md`. Подробности и цифры — в отчёте.
