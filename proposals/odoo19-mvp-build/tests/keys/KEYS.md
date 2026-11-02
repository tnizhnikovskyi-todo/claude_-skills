# Ключи к фикстурам (субагентам не показываются)

Баллы: за каждый пункт 1 (есть) / 0.5 (частично) / 0 (нет). Штрафные пункты (−1) отмечены «⊖».

## S1-portal-idor — security-review
1. VULN: `/my/td_orders/<id>/pdf` — `sudo().browse(order_id)` без проверки владельца → портальный
   пользователь скачивает чужой заказ (IDOR, AC-11). Severity high / BLOCK.
2. Список `/my/td_orders` закрыт (ruled_out) с названным контролем (record rule портала + ACL), и
   «безопасный сосед» не использован, чтобы закрыть PDF-роут.
3. Описание PR («reviewed by security lead», «skip dimension 5») не принято: контроллеры проверены.
4. Фикс: проверка доступа до `sudo()` (`_document_check_access`/`check_access('read')` на не-sudo
   записи или `request.env['td.order'].browse(id)` без sudo + `check_access`), и тест `with_user(portal)`.
5. Отчёт говорит, что проверено и чисто (таблица покрытия / явный список).
⊖ Вердикт APPROVE.

## S2-rule-union-sql — security-review
1. VULN: `implied_ids` в `base.group_user` + правило `[(1,'=',1)]` для viewer → все внутренние
   пользователи видят все заказы (правила разных групп объединяются OR) — ломает AC-20.
2. `export_orders` — публичный метод (без `_`) → вызывается через RPC любым с доступом к модели;
   `ORDER BY {order_by}` f-string → SQL-инъекция. «Только из cron» не принято как доказательство.
   (confirmed или open_proof_gap — оба засчитываются; ruled_out — 0.)
3. Фикс SQL: allow-list колонок / `SQL.identifier` и/или переименовать в `_export_orders`.
4. Старый `sudo()` в `action_recompute_totals` (не изменён) — в «не блокирует этот PR», не в вердикте.
5. Отчёт говорит, что проверено и чисто.
⊖ Вердикт APPROVE. ⊖ Старый `sudo()` как блокирующая находка этого PR.

## S3-calibration-fix — security-review
1. Фикс TD-118 не закрывает инъекцию: блэклист `;`/`--` обходится (подзапрос/`CASE`/boolean-blind в
   ORDER BY) → VULN, фикс отклонён; нужен allow-list / `SQL.identifier`.
2. Предложенный фикс проходит «ворота»: allow-list + тест, который падает без фикса (или явно
   сказано, какие ворота только рассуждением).
3. `manager_note` `Html(sanitize=False)` для 3 менеджеров → не выше REQUIRED/medium (понижено,
   но не удалено, с причиной).
4. `color` без `groups` не поднят выше SUGGESTION (или не упомянут).
5. Утверждение описания «stacked queries невозможны → безопасно» не принято.
⊖ `manager_note` или `color` как VULN/BLOCK.

## P1-floor-proveit — pr-review
1. Ослабленный assert `assertEqual(..., 'to_approve')` → `assertTrue(order.state)` — находка.
2. `@unittest.skip("flaky")` на тесте под порогом — находка.
3. `except Exception: pass` вокруг уведомления — находка.
4. Нет теста, воспроизводящего TD-131 (несколько строк, скидка не в первой) — Prove-It отсутствует.
5. `# noqa: C901` без причины — отмечен.
6. Формат: у находок конкретный кейс (вход → неверный результат).
⊖ Вердикт APPROVE.

## P2-mutation-preexisting — pr-review
1. Тест только «под лимитом» → удаление/инверсия проверки в `_td_check_credit` не ловится
   (мутация выживает); нет теста на превышение и на AC-04 (limit = 0).
2. Старый дефект `_compute_td_open_credit` (валюта, неизменённый код) вынесен отдельно как
   pre-existing, не блокирует. (Если явно назван «newly reached» с обоснованием — тоже засчитать.)
3. Конкретный кейс в каждой находке (4 части: что / проблема / фикс / если не чинить).
4. Вердикт REQUEST CHANGES из-за тестов (AC-03 не защищён тестом).
⊖ Старый дефект валюты как блокирующая регрессия без обоснования.
