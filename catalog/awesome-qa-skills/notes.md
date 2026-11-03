# awesome-qa-skills — рабочий журнал

## 2026-11-03

**Клон.** `naodeng/awesome-qa-skills` склонирован в scratchpad (вне нашего
репо), только чтение. Разобран коммит
`fc10ba17bd3ffeeeeeea77104f9e7ab8739723b6` (main, 2026-11-03 18:05 +0800).
Ничего не запускали: ни установщики, ни `scripts/`, ни `.githooks/`, ни evals.

**Объём.** 210 коммитов с 2026-02-05, 203 от одного автора (Nao), 65 коммитов
с 1 октября. ~9 тыс. файлов. 338 `SKILL.md` = ~169 скиллов × 2 языка
(`skills/en`, `skills/zh`): `testing-types` (150), `testing-workflows` (14),
`skill-engineering` (5). Плюс `installers/` (по обёртке на каждый скилл × 6
агентов × mac/win), `evidence/` (1639 файлов прогонов), `docs/`, `tests/`.

### Лицензия (поиск дал NOASSERTION)

- Файл `LICENSE` на SHA — **PolyForm Noncommercial 1.0.0**. GitHub/licensee
  этот текст не распознаёт, отсюда NOASSERTION.
- Во frontmatter каждого `SKILL.md`: `license: PolyForm-Noncommercial-1.0.0`.
- История `LICENSE`: `3167fa9` 2026-04-25 создан (GPL-3.0) → `03fc0aa`
  2026-08-14 CC BY-NC-SA 4.0 → `be33634` 2026-08-16 PolyForm NC. До
  2026-04-25 лицензии не было вовсе.
- «Required Notice:» строк нет. Внешние скиллы из «community list» в README
  в репозиторий не вложены (только ссылки), у них свои лицензии.
- **Вывод.** Мы коммерческая компания (внедрения Odoo для клиентов); наш
  репозиторий публичный под MIT. PolyForm NC коммерческое использование
  запрещает. Старые версии под GPL-3.0 теоретически доступны, но GPL
  несовместима с нашей MIT-публикацией без смены лицензии, а
  текст за 2026-04…08 отличается от разобранного. Решение: **только идеи
  своими словами**, никаких цитат, шаблонов, промптов, имён разделов 1:1.

### Безопасность

- Установщик `scripts/install-skills-mac.sh` (+ `.ps1`, + обёртки в
  `installers/`): копирует выбранные каталоги скиллов в `~/.claude/skills`
  (`~/.cursor`, `~/.codex`, …) через `rsync -a --delete` по каждому каталогу
  скилла. Сети нет, но `--delete` перезапишет одноимённый наш скилл.
- `.githooks/pre-commit` — только локальная проверка качества; ставится
  вручную (`core.hooksPath`).
- `scripts/` внутри скиллов: конвертеры форматов (csv/xlsx/docx/xmind),
  парсеры. Сетевые вызовы (`curl`, HTTP) только в API/перф-скиллах
  (`api-test-*`, `performance-test-k6/gatling`) — по назначению, для
  прогонов против тестируемого API. Телеметрии нет (grep по
  telemetry/analytics/sentry/posthog пусто).
- CI: `plugin-security-scan.yml` (сторонний HOL Plugin Scanner, пин по SHA),
  `project-quality.yml`; `persist-credentials: false`.
- Хуков Claude Code, `.mcp.json`, MCP-серверов в поставке нет.

### Что прочитали

`SKILL.md` + `prompts/*.md`: `test-case-writing`, `testcase-writer-plus`,
`manual-testing`, `acceptance-criteria-review`, `bug-reporting`,
`regression-scope-analysis`, `quality-gate-design`, `test-reporting`,
`production-verification`; workflows `requirement-to-test`,
`release-testing-workflow` (+ `workflow.yaml`). Шаблоны
`output-templates/template-markdown.md` (общие, слабые). `evals/eval.yaml`
(движок `skill-up`, кейсы yaml). `evidence/.../2026-10-05-codex-benchmark-repeat`.

### Собственный A/B автора (важно)

В `evidence/skill-quality/2026-10-05-codex-benchmark-repeat/README.md`
автор честно опубликовал with/without по 3 прогона на модели GPT:
`functional-testing` 3/3 vs 3/3 (**прироста нет**), `testability-analysis`
3/3 vs 2/3, `skill-evaluation` 3/3 vs 0/3 (только соблюдение формата
состояний). Совпадает с нашим `synthesis.md` п. 2 и 1: базовый тест-дизайн
модель делает и так; прирост там, где скилл задаёт формат/статусы, которых
у модели нет. На Claude прогонов нет.

### Сравнение с приватными плагинами

`add_repo` на чтение `todoltd/claude-methodology-marketplace` **отклонён**
классификатором прав сессии. Сравнение с `odoo19-mvp-build:testing`,
`odoo19-implementation:acceptance-act-builder` / `hypercare-tracker` —
только по описаниям из `inventory/current.md`, списка скиллов сессии и
карточки `catalog/generate-test-book/`. Из приватного репо ничего не
копировали. Перед реализацией T11 сверить с текстами этих скиллов.

### Решения

- Чужие скиллы не запускали, A/B на наших задачах не делали (нужно
  разрешение; и брать их как есть нельзя по лицензии).
- Вердикт: **адаптировать (только идеи)**, в первую очередь в T11.

### Открытые вопросы

1. Устраивает ли вариант «только идеи» или пользователь хочет связаться с
   автором ради коммерческой лицензии (не нужно, на мой взгляд).
2. Тексты `acceptance-act-builder`, `hypercare-tracker`, `testing` — нужен
   доступ к приватному репо, чтобы точно сказать, что дублируется.
