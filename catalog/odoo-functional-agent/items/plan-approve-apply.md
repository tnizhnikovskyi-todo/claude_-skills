# Цепочка план → одобрение → freeze → apply

- **Источник:** `skills/odoo-functional/SKILL.md`, `skills/odoo-functional/plan_md_template.md`,
  `docs/plan_format.md`, `src/ofa/executor.py`, `src/ofa/plan.py` @ `084b690`
- **Вердикт:** адаптировать формат и правила в `config-spec`/`config-runbook`
  и в демо-цепочку продаж

## Что делает

8 фаз: Preflight (`ofa doctor`, сервер, демо-база) → Intake (требование дословно,
анонимизация реальных имён/налоговых номеров, ≤3 вопроса только о том, что меняет
конфигурацию) → Plan → Review stop → Apply → Test → Evidence → Report.

**План** — `plan.json` (`ofa.plan/1`): операции `install_modules`, `set_settings`,
`upsert_record` (с `key` → внешний id `__ofa__.<key>`, `match` для «усыновления»
существующей записи, в т.ч. архивной), `call_method` (обязателен `skip_if`, иначе
повтор не идемпотентен). Общие поля: `id`, `depends_on` (топосортировка), `rationale`
одной строкой, `knowledge_refs`, `edition`, `company`. Ссылки `$ref`/`$search`/`$set`/`$add`,
`$create` в плане запрещён. `plan.md` — по шаблону, каждый `[op_id]` обязан
встречаться в тексте (`OP_NOT_IN_PLAN_MD`).

**Стоп ревью.** Показать весь plan.md с Test plan, список операций, «Names to review»
из линтера и ждать явного одобрения. Правила (дословно по смыслу):
- вопрос, комментарий, молчание или одобрение прошлой версии — не одобрение;
- ранее сказанное «сделай всё» — не одобрение;
- любая правка plan.json или решения в plan.md → `validate` + `lint-plan` заново,
  показать изменения, ждать нового одобрения;
- сообщение одобрения сохранить и процитировать в отчёте.

**Apply.** `ofa freeze` пишет SHA-256 канонического JSON плана; `ofa apply` без
`plan.approved` → `NOT_APPROVED`, с изменённым планом → `HASH_MISMATCH` (до любого
вызова Odoo). Статусы: `created | updated | adopted | unchanged | called | failed |
skipped`; первая ошибка останавливает прогон. После каждой записи — чтение назад
(`VALUE_NOT_HELD`, если Odoo пересчитал значение). `pre_state: true` — операция была
`unchanged` уже на первом применении, т.е. состояние было в шаблоне и **ничего не
доказывает**. Ошибка в отчёте — только `имя: сообщение`, без traceback и путей.
Повторный apply того же плана → всё `unchanged`.

**Отчёт:** цитата одобрения и run id; счётчики статусов с выделением `pre_state`;
Test plan с колонкой результата и списком расхождений; что делается только в UI
(с путём меню); все решения без источника; «What you learned» в бизнес-терминах;
предложение удалить базу — только по «да».

## Сравнение с нашим

- `demo-base-builder` уже требует согласованный план, поиск перед созданием,
  проверку следствия, «не имитируй запись». Не хватает: хеша/версии одобренного
  плана, явных правил «что не является одобрением», `pre_state`.
- `config-spec`/`config-runbook` (код не читали) — сверить: есть ли у нас
  `rationale` на операцию, `skip_if` для методов, ссылка на источник на решение,
  блок «Not covered».

## Что переносим

1. Правила одобрения (список выше) → `config-runbook` и `demo-base-builder`.
2. Шаблон решения: Ops / Decision / Business reason / What Odoo does / Pre-state /
   Alternatives / Pitfalls / Sources (или «Uncited: …») + «Not covered by this plan»
   + «Glossary» → `config-spec`.
3. Хеш одобренного плана (sha256 канонического JSON или файла плана) в шапке
   плана и в отчёте/знімке; несовпадение → стоп.
4. `pre_state` → в знімок и `config-review`: «уже было до нас».

## Атрибуция

Перевод/адаптация с атрибуцией: xmglord/odoo-functional-agent @ `084b690`,
`skills/odoo-functional/SKILL.md`, `plan_md_template.md`, `docs/plan_format.md`, MIT.
