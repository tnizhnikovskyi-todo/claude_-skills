# Предложение: правило `siblings_checked` для семей плагинов (задача 3.5)

Источник идеи: `catalog/one-skill-to-rule-them-all/` (task-observer,
CC BY 4.0). Скиллы одной семьи передают друг другу файлы и ID. Правка
формата в одном молча ломает соседа, который этот формат читает.

## Правило (вставить в CLAUDE.md репозитория плагинов)

```text
Правишь скилл из семьи (odoo19-*, tr-*, discovery, sales) — до коммита
проверь соседей по карте ниже: кто читает то, что этот скилл пишет, и кто
пишет то, что он читает. В описании коммита/PR строка:
siblings_checked: <скилл-1>, <скилл-2> — <что проверено> | нет соседей.
Изменились имя файла, раздел, ID-префикс (D-/X-/Q-/C-/T-/A-/G-/P-/R-) или
поле, которое читает сосед: правь соседа в том же PR или объясни, почему
не нужно.
```

## Карта соседей (по описаниям скиллов в окружении, 2026-11-02)

Описания взяты из списка установленных скиллов. Тексты `odoo19-*` в
окружении не найдены (см. `reports/review-upgrades.md`,
`reports/discovery-interview.md`), поэтому карту стоит сверить с
оригиналами.

| Семья | Цепочка (кто → кому передаёт) | Общие форматы |
|---|---|---|
| Продажи `odoo19-sales-*` | `brief-prep-pack` → бриф → `brief-transcript-analyzer` (журнал продажу) → `client-followup-writer`, `data-completeness-scorer` → `preliminary-estimate` → `demo-build-plan` → `demo-base-builder` → `demo-runbook` → `presale-pack-builder` → демо → `demo-debrief` / `demo-followup-writer` / `client-questions-pack` → `offer-finalizer` → `defence-brief` → `defence-debrief` → `handover-dossier-builder`; `deal-revival-check`, `loss-pattern-analyzer` читают журнал | `журнал_продажу_[компания].md`, реестры D/X/G/Q/C/P/R/A-N, коэффициент вилки |
| Дискавери `odoo19-discovery-*` | `sales-handover-analyzer` (читает досье передачи) → `kickoff-question-builder` → `kickoff-agenda-finalizer` → `kickoff-transcript-analyzer` → `discovery-plan-builder` → `session-question-builder` → `session-client-prep-builder` → `session-transcript-analyzer` → `discovery-scope-mapper` → `discovery-gap-analyzer` → `discovery-report-builder`, `discovery-sow-builder`, `journal-to-tr-builder`; `meeting-protocol-builder` на любой встрече | `журнал_дискавері_[компанія].md`, D/X/C/T/Q/A-N, `scope_`, `gap-аналіз_` |
| ТР `odoo19-tr-authoring:*` | `journal-to-tr-builder` (секция 1) → `tr-usecases-acceptance` (секция 2) → `tr-odoo-tech-design` → `tr-effort-instruction` → `tr-review` → `tr-registry-update`; `tr-change-request` | `ТР_[назва].md`, `origin:` backref, реестр ТР |
| Сборка `odoo19-mvp-build:*` | `spec-writer` → `architecture` → `build-allocator` → `scaffolding` → `code-dev` / `config-spec` → `config-runbook` → `testing` → `pr-review`, `config-review`, `security-review` → `track-convergence`; `reverse-spec` | SPEC/AC, гейты APPROVE/BLOCK |
| Внедрение `odoo19-implementation:*` | `data-migration-planner` → `go-live-runbook` → `hypercare-tracker` → `acceptance-act-builder`; `user-training-builder` | AC из SPEC/ТР, реестр |
| Наш `boost` | `cloud-memory` ↔ `skill-feedback` (формат frontmatter), `odoo-model-map` ↔ `repo-audit` (шаг «карта модуля»), `source-check` ↔ шаблон `CLAUDE.md` (правило Context7) | `memory/`, `observations/` |

## Уже известные пары для наших предложений

- `proposals/odoo19-discovery/` (поле «Наша гіпотеза»): проверить
  `session-client-prep-builder` (не переносить гипотезы в письмо клиенту) и
  `session-/kickoff-transcript-analyzer` (читать «Підтвердити:» и
  «Підсумок для підтвердження»).
- `proposals/odoo19-mvp-build/security-review/` (новое правило вердикта
  `open_proof_gap` → не APPROVE): проверить `track-convergence` и
  `pr-review`, которые читают вердикт.
- `proposals/odoo19-mvp-build/pr-review/` (метки regression /
  pre-existing): проверить `track-convergence`.

## Как проверить, что правило работает

Барьер вместо обещания: грейдер или CI-проверка «в описании PR есть строка
`siblings_checked:`», если изменён файл `skills/*/SKILL.md`.
