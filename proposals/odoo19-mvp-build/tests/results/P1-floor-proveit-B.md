# P1-floor-proveit — предлагаемый текст (B)

Субагент не записал OUTPUT.md (сказал, что у него нет шага записи). Ниже — его ответ в сжатом
пересказе главной сессии, без изменения сути.

- Вердикт: REQUEST CHANGES. Ядро фикса (max по строкам) корректно для AC-05.
- SUGGESTION-1: `_td_notify_manager()` не из SPEC и стоит не в той ветке (4 части, Origin: regression).
- REQUIRED-1: `except Exception: pass` — нарушение «пола»; предложен `savepoint` + `_logger.exception`.
- REQUIRED-2: `# noqa: C901` без причины/владельца — нарушение «пола».
- REQUIRED-3: `assertEqual(..., 'to_approve')` → `assertTrue(order.state)`; конкретный кейс: 20% при лимите 10% проходит при любом state.
- REQUIRED-4: `@unittest.skip("flaky on CI")` без владельца/срока; тест покрывает ветку «в лимите → sale».
- REQUIRED-5: нет Prove-It; показано, что существующий тест ([20.0]) прошёл бы и на base; предложен `[5.0, 15.0]` при лимите 10.
- Раздел «Quality floor»: 4 попадания, исключений нет.
- Таблица мутаций (static): возврат к `order_line[:1]` — SURVIVED; `>`→`<=` — SURVIVED (единственный ловящий тест пропущен); `>=` на границе — SURVIVED.
- «Pre-existing (not blocking)»: прямая запись `state`, пустой лимит.
- «Not checked»: тесты не запускались, `_td_notify_manager`/`_make_order` не прочитаны, нет git blame.
- Все находки в формате 4 частей.
