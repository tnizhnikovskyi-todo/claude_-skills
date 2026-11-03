# buyer-eval — рабочий журнал

## 2026-11-03

**Задача от главной сессии:** скилл со стороны покупателя; что из него
взять в `defence-brief`, `presale-pack-builder`, `demo-runbook`,
`offer-finalizer`; отдельно — нет ли маркетинговой воронки вендора.

### Что смотрели

- Клон `salespeak-ai/buyer-eval-skill` в scratchpad, `HEAD`
  `ebb0e069ec007d94ff68a3d0f4ee0c37a3450423` (v4.1.1, 2026-09-28).
  Ничего не запускали.
- Прочитаны полностью: `SKILL.md`, все `references/*.md`, `bin/track.py`,
  `bin/update-check`, начало `bin/profile.py`, `MEASUREMENT.md`,
  `CHANGELOG.md`, `EVALUATION.md` (заглушка v4), `README.md`, `LICENSE`.
  `bin/render_report.py` — поиск сети (`http|urllib|requests|subprocess|socket|curl`):
  только проверка схемы URL, вывод через `html.escape`.
  `promo/video-src/voice/generate.sh` — `curl` в ElevenLabs по ключу,
  к скиллу не относится.
- История: 27 коммитов, один автор (`omer@salespeak.ai`), март–апрель и
  28.09.2026. Старый `EVALUATION.md` (v3.5, `03b18a4`) — для сравнения
  нейтральности.
- `sale_todo_claude` @ `2a7f7c1`: заголовки и ключевые шаги `defence-brief`,
  `offer-finalizer`, `presale-pack-builder`, `demo-runbook`,
  `client-questions-pack`; Крок 1–3 `defence-brief` и Крок 3 `demo-runbook`
  целиком; поиск по всем `SKILL.md` и `shared/` тем «референс», «SLA/
  підтримка», «хостинг/безпека», «ліцензії», «статус-кво», «подорожчання».
- Карточки `lmty-skills`, `mastering-technical-sales`, `presales-agent-skill`,
  `ai-presales-skills` (summary), `roadmap.md` T10, `synthesis.md` (3-й проход, п. 3).

### Что проверили

- **Лицензия:** `LICENSE` — MIT, Copyright 2026 SalesPeak. Совпадает с
  поиском. Признаков чужого текста (книги, плейбуки) нет.
- **Сеть без согласия:** `discover` (GET на Lambda Salespeak) — «Always run
  it» в `quick-eval.md` Q3; `chat` (POST) — вопросы агенту вендора;
  `update-check` — `curl` GitHub raw с кэшем 6 ч. README честно пишет
  «What leaves your machine without asking».
- **Воронка:** `MEASUREMENT.md` — discover как «consent-independent run
  count», «Group by source IP and hour… exclude Salespeak IPs» (статус «not
  yet verified»). Телеметрия: `vendor_question.question_text`,
  `discovery_question_asked.question_text`, `eval_context.vendors`,
  `eval_completed.leading_vendor` — Salespeak узнаёт, каких вендоров
  сравнивают, какие вопросы задают покупатели и кто лидирует. Постоянный
  `user_id` связывает запуски.
- **Нейтральность в истории:** v3 (`03b18a4:EVALUATION.md` стр. 352): «treats
  the Company Agent as the authoritative source»; «Evidence Completeness
  Score: X/7 dimensions with verified (vendor-confirmed) evidence» —
  выгодно вендорам с агентом Salespeak. v4.0.0 убрал, CHANGELOG это
  признаёт; там же: тесты показали, что v3 отправлял агенту вендора потолок
  бюджета покупателя.
- **v3.5** (README той версии): «Existing consented users keep flowing data
  with no re-consent» при расширении событий.
- **Покрытие у нас:** в пяти скиллах нет референсов, SLA/поддержки после
  запуска, хостинга/данных, роста цены лицензий при продлении, устойчивости
  интегратора. В `client-followup-writer/assets/docx-boilerplate/про-todo.md`
  есть «Команда 65+ співробітників» и «надаємо підтримку… впродовж усієї
  співпраці» — для покупателя это заявления без подтверждения.
- **Что уже есть у нас и сильнее:** заперечення по фактам проекта, межа
  торгу, обещания `P-N` и дифф версий КП, отбор ≤ 7 / ≤ 12, «не пишемо
  типові питання з голови».

### Решения

- Вердикт «адаптировать точечно», 8/18; скилл не ставить и не запускать.
- `items/`: три карточки (компоненты одного скилла, но с разным назначением):
  `evidence-model.md`, `buyer-diligence-questions.md` (черновик вставки под
  Odoo), `data-flows.md` (воронка).

### Открытые вопросы

- A/B для вставок 1–2 (`defence-brief` с колонкой «як це побачить клієнт» и
  списком измерений закупки) — не делали.
- Есть ли у ToDo публичные условия поддержки/SLA и кейсы с контактом
  референса — от этого зависит, чем отвечать на п. 2 банка вопросов.
- Правки в `sale_todo_claude` — через главную сессию / PR владельцу.
