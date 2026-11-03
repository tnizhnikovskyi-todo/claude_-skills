# security-harness — рабочий журнал

## 2026-11-03 — первичный разбор

**Источник:** https://github.com/dmdhrumilmistry/security-harness
**Коммит:** `68748d52c99e10d09e7709d62fd78375ad8148fc` (2026-09-27, merge PR #12). Лицензия MIT.
Клон в scratchpad, вне нашего репозитория. Ничего не запускалось: ни харнесс, ни агенты,
ни скрипты, ни установщики. Только чтение.

### Что смотрели

- `README.md`, `CLAUDE.md`, `AGENTS.md`, `docs/DISTRIBUTION.md` (бегло).
- `skills/` в корне — зеркало `plugins/security-harness/skills/` (проверено `diff -rq`: идентично,
  генерируется `scripts/sync-agent-skills.py` для Codex/opencode/Gemini).
- Оркестратор `sh-security-review/SKILL.md`, роутер `sh-router/SKILL.md`.
- 5 агентов: `sh-recon`, `sh-hunter`, `sh-chainer`, `sh-verifier`, `sh-reporter`.
- `references/`: `severity-rubric.md`, `attack-surface-checklist.md`, `state-files.md`,
  `finding-schema.json` (поля `status`, `pr_impact`), `graft-guide.md`, `tooling-setup.md`,
  `pr-review-mapping.md` (34 КБ: триаж, тиры, якоря, отпечатки, стиль комментариев, вердикт).
- `sh-pr-review/SKILL.md` целиком (39 КБ) и импорты трёх Python-скриптов.
- Один KB целиком: `sh-kb-access-control`. Остальные 14 — по размеру и заголовкам
  (3–7 КБ каждый, общий шаблон).
- `.github/workflows/update-knowledge-base.yml`, `kb-review-and-merge.yml`, `kb-update/*`.

### Что проверили

- **Сеть в скриптах.** `sh-metrics.py`, `sh-review-cache.py`, `sync-agent-skills.py` — только
  stdlib без сетевых модулей. `sh-pr-post.py` вызывает `gh` через `subprocess` (постит ревью и
  commit status). Телеметрии нет, метрики локальные, токены редактируются перед записью.
- **Установки.** Stage 0 полного ревью сам ставит `npm install -g @nanonets/graft`, затем
  `syft`/`grype`/`trivy`/PDF-движок через пакетный менеджер или `curl ... install.sh | sh`
  (с ветки `main` вендора, без пина версии). Только «объявляет», не спрашивает. `sudo`
  допускается, «если платформа требует».
- **Запись в чужой репозиторий.** `graft init <target>` пишет в цель `.mcp.json`,
  `.claude/settings.json`, `.claude/helpers/*.cjs` (хуки), `.claude/skills/graft/SKILL.md`.
  Отказ — «если пользователь откажется», явного вопроса нет.
- **Постинг на PR.** Описание `sh-pr-review` (frontmatter): «never posts without an explicit yes».
  Тело скилла, Phase 7: «Posting is the default… `--confirm` restores the prompt». README
  противоречит сам себе в двух абзацах. Фактическое поведение — постит без вопроса и ставит
  commit status. Для нас это внешнее действие без подтверждения.
- **Самообновление KB.** Раз в два дня агент в GitHub Actions читает веб (allowlist доменов,
  включая `hackerone.com` и весь `github.com`), правит `sh-kb-*`, второй агент-ревьюер решает,
  автослияние в `main` при APPROVE. Человек в цепочке только если владелец включил branch
  protection. Установленный из маркетплейса плагин тянет `main` → текст промптов меняется без
  нашего ревью. Защиты продуманы (fail-closed ревьюер без shell и веба, отказ для форков,
  префикс веток), но это всё равно цепочка поставки промптов.
- **Активность.** 34 коммита, 2026-08-22 … 2026-09-27, один автор, ★42. Пять недель без коммитов
  на дату разбора. Тестов и evals в репозитории нет: качество ревью автор не измеряет, только
  стоимость (`sh-metrics.py`).

### Сравнение с нашим `security-review`

Наш текст лежит в `proposals/odoo19-mvp-build/security-review/proposed/` (в
`~/.claude/plugins/synced/` в этой сессии пусто). Там уже есть из Strix: closure states,
что НЕ доказывает безопасность, калибровка severity, 5 ворот фикса, diff-scope, таблица
покрытия, «Noted, not blocking this PR».

Дублирует (не переносим): verifier «refute first» (= counterevidence), `needs-runtime`
(= `open_proof_gap`), severity independent of confidence (= «unknown exposure lowers
confidence, not severity»), рубрика severity (у нас Odoo-вариант лучше), «описание PR —
недоверенный ввод».

Сверх перенесённого (кандидаты):
1. `pr_impact` = `introduced` / `aggravated` / `pre_existing` с **закрытым списком критериев**
   для `aggravated` и правилом «не уверен → нижний ярлык». Наш `diff-scope.md` покрывает
   3 из 5 критериев (reachability, guard weakened, частично input surface), но не
   «newly chainable» и «blast radius increased», и не даёт тай-брейка.
   Плюс правило `introduced`: «уязвимая строка — добавленная, **или стоит в функции,
   содержащей добавленную**». Это ровно закрывает открытый вопрос из нашего
   `tests/results/SCORES.md` (P2): «новый код, повторяющий старый дефект, — regression?».
2. **Триаж по тирам до запуска агентов** (path-globs + токены в добавленных строках →
   Tier 0–3, Tier 0 = ноль субагентов). У нас критики (П20) запускаются «optional» без правила,
   когда. Для Odoo нужны свои сигналы, их глобы веб-фреймворков не подходят.
3. **Стиль комментария к находке**: таблица «slop → что писать» (механизм вместо категории,
   фикс кодом, как достигается, без хеджей и эмодзи). Полезно и для `pr-review`.
4. Отпечаток находки без номера строки (`cwe|path|нормализованный сниппет`) + раздел
   «Resolved since the last review». У нас есть итерации критиков (до 2), но нет способа
   сказать, что исправлено. Только идея — мы не постим на PR.
5. Chainer: «повышение severity цепочки» и «promote pre_existing → aggravated, если цепочка
   содержит introduced». Нам — только как критерий в пункте 1.

### Почему мультиагентность тут другая, чем `independent-check`

`independent-check` = второй взгляд на ту же задачу → Δ = 0 (модель и так находит, если
попросить). Здесь агенты делят **ширину**: по агенту на класс уязвимостей со своей KB, плюс
отдельный верификатор и тиринг моделей ради цены. Это может помочь на **полном аудите
большого кода**, где один контекст не держит 15 классов. На наших задачах (диф одного
`td.*` модуля) базовый скилл уже даёт 13.5–15/15 одним агентом (`SCORES.md`), а у харнесса
нет знаний Odoo (ACL CSV, `ir.rule`, `sudo()`, `auth=` в `@http.route`): `sh-kb-access-control`
про Express/Django/Spring. Ожидаемый прирост на наших дифах ≈ 0 при цене ×5–10. Не измерено.

### Оценка стоимости (не измерена, оценка)

Полный прогон: recon (sonnet) + до 15 охотников (4 haiku, 8 sonnet, 3 opus) + chainer (opus) +
verifier (opus) + reporter (haiku). При наших ~70–90k токенов на субагента (`SCORES.md`) это
порядка 1–1.5M токенов. PR-ревью: Tier 1 — 1 агент, Tier 2 — 3–6, Tier 3 — 6–10.

### Открытые вопросы

- A/B: стоит ли переносить `pr_impact`-критерии и Odoo-триаж — прогнать на фикстурах
  `proposals/odoo19-mvp-build/tests/fixtures/` (S1–S3, P2) вариант «с критериями» против
  текущего proposed. Нужно разрешение пользователя (запуск субагентов на наших текстах).
- Нужна ли нам «ширина по классам» для полного аудита, а не дифа (например, перед go-live
  клиента)? Если да — это отдельный скилл, и только после A/B.

## 2026-11-03 — уточнение после сообщения главной сессии

Главная сессия подсказала, где тексты наших плагинов. Для сравнения хватило нашего репо:
`proposals/odoo19-mvp-build/security-review/{current,proposed}` и `pr-review/proposed`.
Приватный `todoltd/claude-methodology-marketplace` не подключали: для этого разбора он не
нужен (сравниваем только `security-review` и `pr-review`, оба есть в `proposals/`).

**Поправка к п. 1 сравнения.** В proposed `pr-review` (`references/review-discipline.md` §4)
уже есть три метки: regression / newly reached / pre-existing, с двумя критериями (строка
изменена; первый вызывающий / новый роут / новое поле). Значит, у security-harness новое
только:
- критерии «guard ослаблен», «input surface шире», «newly chainable», «blast radius ↑»
  (первый у нас есть в `security-review/diff-scope.md`, но не в `pr-review`);
- `introduced` включает «функцию, содержащую добавленную строку» (ответ на P2);
- уклон при сомнении: у них «→ pre_existing», у нас «never relabel a regression as
  pre-existing». Противоположные приоритеты (шум гейта против пропуска), решать A/B,
  а не вкусом.
Оценка прироста методики — без изменений (2), но объём переноса меньше: ~5–8 строк, а не раздел.
