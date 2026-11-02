# Наблюдения к скиллам

Поправки пользователя и нарушения правил наших скиллов. Пишет скилл
`skill-feedback` (плагин `boost`) по поправке или явной просьбе; раз в
неделю главная сессия сводит открытые наблюдения в правки скиллов.
Скилл и сессии, которые записывают наблюдения, сами скиллы не правят.

Основа: task-observer (`catalog/one-skill-to-rule-them-all/`, CC BY 4.0),
упрощённо: без фонового триггера, без скриптов и хуков.

## Формат

Файл `YYYY-MM-DD-<skill>-<slug>.md`, по одному на наблюдение.

```markdown
---
skill: repo-audit
date: 2026-11-02
status: open            # open | actioned | declined | superseded | parked
kind: gap               # correction | violation | gap
fix: text               # text | barrier | unknown
rule: "ir.rule у дочерних моделей"
repeat_of: null         # файл прошлого наблюдения о том же правиле
siblings_checked: ["security-review: ?"]   # имя: ok | same | ?
source: pilot-notes/README.md
summary: Одна фраза до ~120 символов
resolution: ...         # ставит ревью при смене статуса
---
**Ожидали:** …   (Issue)
**Получили:** …  (Issue)
**Предложение:** … (Improvement)
**Принцип:** …   (Principle или «—»)
```

Поля и статусы подробно:
`plugins/boost/skills/skill-feedback/references/format.md`.

Без секретов, клиентских и персональных данных: папка в git.

### Второе нарушение → барьер

Если по тому же `skill` и `rule` уже есть наблюдение (`open`, `actioned`,
`parked`), новое получает `repeat_of` и `fix: barrier`. Лечим не новой
формулировкой, а механической проверкой: eval-кейс/грейдер, проверка в
скрипте скилла, хук, пункт чек-листа, который проверяется командой.

## Еженедельное ревью (главная сессия)

Полная процедура: `plugins/boost/skills/skill-feedback/references/weekly-review.md`.

1. **Сбор:** `grep -l 'status: open' observations/*.md` и наблюдения из
   веток `build/*`.
2. **Классификация:** прочитать тела; сгруппировать по `skill`, внутри по
   `rule`. Решение по группе: правка текста / барьер (обязателен при
   `repeat_of` или ≥ 2 записях об одном правиле) / отказ (`declined`) /
   ждёт условия (`parked`) / покрыто другим (`superseded`). Проверить
   `siblings_checked`.
3. **Сводка пользователю** таблицей; решения по спорным строкам даёт
   человек.
4. **Правка** одобренного: ветка `build/fix-<skill>-<дата>`,
   `anthropic-skills:skill-creator`, для барьера сначала кейс, который
   падает на старой версии; `claude plugin validate plugins/boost`.
5. **A/B до слияния:** `claude plugin eval plugins/boost --case '<skill>/*'
   --runs 3 --max-cost-usd 5 --no-publish --scaffold --trust-plugin -j 4
   --judge-model sonnet`; итог в `reports/fix-<skill>-<дата>.md`. Без
   прироста или с регрессией не сливать.
6. **Статусы:** `status` и `resolution` в наблюдениях, коммит
   `observations: review <дата>`.

Готовый текст промпта для запланированной еженедельной задачи: в конце
`weekly-review.md`. Саму задачу создаёт главная сессия.

## Текущие наблюдения

Засеяны из отчётов первой волны (2026-11-02):

| Файл | Скилл | Суть | fix |
|---|---|---|---|
| `2026-11-02-repo-audit-child-ir-rule.md` | repo-audit | K12: нет `ir.rule` мультикомпании у строк заказа | text |
| `2026-11-02-repo-audit-empty-group.md` | repo-audit | K15: пустая группа менеджеров, со скиллом пропущена | text |
| `2026-11-02-lean-change-odoo-test.md` | lean-change | тест в Odoo-задаче 1–3 из 3 прогонов | text |
| `2026-11-02-source-check-offline-case.md` | source-check | кейс `unverified-offline` не различает плечи | barrier |
| `2026-11-02-source-check-quote-webfetch.md` | source-check | цитата через WebFetch не дословная | unknown (кандидат в parked) |

Таблица для удобства; источник истины это frontmatter файлов.
