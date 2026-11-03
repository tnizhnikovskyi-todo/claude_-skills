# Журнал разбора: opencode-power-pack

Дата: 2026-11-03. Сессия анализа, ветка `analysis/opencode-power-pack`.

## Что смотрели

- Клон `https://github.com/waybarrios/opencode-power-pack` в scratchpad,
  HEAD `c3328ad1633c1561026532f29b718a2380bc52ee` (2026-10-27, v0.6.0).
  117 коммитов с 2026-04-26, последний 2026-10-27. Ничего не запускали:
  ни `npm`, ни тесты, ни sandbox-CLI, ни eval-раннер.
- Прочитаны: `README.md`, `package.json`, `.claude-plugin/{marketplace,plugin}.json`,
  `skillsets.json`, `UPSTREAMS.json`, `THIRD_PARTY_NOTICES.md`, `LICENSES/`,
  `.opencode/plugins/opencode-power-pack.js` (начало), `evals/behavioral/*`,
  `scripts/behavioral-evals.mjs` (начало).
- Скиллы прочитаны целиком или по разделам: `fp-check` (+ `gate-reviews.md`,
  `false-positive-patterns.md`), `differential-review`, `insecure-defaults`,
  `supply-chain-risk-auditor`, `agentic-actions-auditor`, `sharp-edges`
  (оглавление), `code-review` (первые 120 строк), `code-quality`,
  `agents-md-revise`, `humanizer` (оглавления и начало).
  Остальные 40+ (Hugging Face, AWS SageMaker, Gradio, ML-тренинг) только
  по `description` и числу файлов: к нашей работе не относятся.
- Для проверки происхождения дополнительно склонированы (только чтение):
  `trailofbits/skills` @ `711af095215ad4ecde5b90cd1d0124b3f1c4ca9e`
  (2026-11-02) и `vigolium/piolium` @ `9ffdcace480f23471ea1f52df7ea01a6a93c1dfd`.

## Главное открытие: это агрегатор, а не автор

Гипотеза из поиска («55 скиллов, ревью и аудит безопасности») верна по
числу, но своих скиллов в пакете **один** (`humanizer`, adaptation
`original`). Остальные 54 по `UPSTREAMS.json`:

| Источник | Скиллов | Лицензия, как заявлено |
|---|---|---|
| `huggingface/skills` | 25 | Apache-2.0 |
| `vigolium/piolium` | 14 (безопасность) | MIT |
| `anthropics/claude-plugins-official` | 8 (`code-review`, `feature-dev`, `agents-md-*`, `frontend-design`…) | Apache-2.0 |
| `anthropics/skills` | 2 (`mcp-builder`, `skill-creator`) | Apache-2.0 |
| `anthropics/claude-code-security-review` | 1 (`security-review`) | MIT |
| `Firstp1ck/pi-coding-agent-forge` | 3 (`code-quality`, `design-patterns`, `paper-summarizer`) | MIT |
| `LePro10/omp-designer` | 1 (`ai-slop`) | MIT |
| свой | 1 (`humanizer`) | MIT |

Вклад автора: обёртка под 4 хоста (Claude Code, Codex, OpenCode 1/2, Pi),
сокращение текстов, «граница недоверенных данных» в скиллах Anthropic,
eval-инфраструктура, sandbox-CLI.

## Лицензия: цепочка рвётся на скиллах безопасности

Проверили, откуда piolium взял скиллы безопасности. Сравнение `diff` тела
`SKILL.md` (без frontmatter) с `trailofbits/skills@711af09`:

| Скилл | Путь в ToB | Изменённых строк / всего |
|---|---|---|
| `sharp-edges` | `plugins/sharp-edges/skills/sharp-edges` | 8 / 289 |
| `fp-check` | `plugins/fp-check/skills/fp-check` | 18 / 112 (только `{baseDir}` и 2 фразы) |
| `differential-review` | `plugins/differential-review/...` | 18 / 211 |
| `semgrep-rule-creator` | `plugins/semgrep-rule-creator/...` | 20 / 161 |
| `agentic-actions-auditor` | `plugins/agentic-actions-auditor/...` | 36 / 323 |
| `semgrep`, `codeql`, `sarif-parsing` | `plugins/static-analysis/skills/*` | переработаны сильнее |
| `supply-chain-risk-auditor`, `variant-analysis`, `semgrep-rule-variant-creator` | есть в ToB | переработаны сильнее |
| `insecure-defaults` | папка `plugins/insecure-defaults` есть, структура другая | не сравнивали построчно |
| `security-threat-model`, `vuln-report` | в ToB не найдены | — |

`trailofbits/skills/LICENSE` = **CC BY-SA 4.0** (Attribution-ShareAlike).
В piolium и в power-pack эти тексты помечены как MIT, Trail of Bits в
атрибуции не упомянут (слово встречается только внутри текстов `codeql` и
`semgrep`). То есть MIT на них, скорее всего, недействителен.

**Решение для нас:** скиллы безопасности считаем CC BY-SA 4.0 от Trail of
Bits. Дословно не копируем (ShareAlike заразил бы наш скилл), берём только
идеи своими словами со ссылкой на ToB. Если когда-нибудь захотим текст —
брать из первоисточника `trailofbits/skills` с атрибуцией и под CC BY-SA.

## Права, сеть, телеметрия

- **Для Claude Code** плагин объявляет только `"skills": "./skills/"`.
  Нет `hooks`, нет `.mcp.json`, нет `settings.json`. Значит, при установке
  сам ничего не запускает. Проверено `find` по всему дереву.
- `allowed-tools` из frontmatter убраны (так сказано в
  `THIRD_PARTY_NOTICES.md`, `grep` подтвердил, что их нет).
- Сеть в текстах скиллов: в основном `huggingface.co`, `github.com`
  (`gh api` в `agentic-actions-auditor` и `supply-chain-risk-auditor`),
  `semgrep.dev`. Команды `curl` (27), `pip install` (15), `uvx` (10),
  `npx` (5) почти все в HF-скиллах. Телеметрии нет (одно упоминание слова
  в тексте, не код).
- Sandbox-CLI (`bin/opencode-power-pack.mjs`, зависимость
  `@anthropic-ai/sandbox-runtime@0.0.73`) ставится отдельно через npm и
  вызывается явно. В Claude Code не подключается автоматически. Не
  запускали.
- OpenCode-плагин (`.opencode/plugins/*.js`) регистрирует скиллы и
  read-only субагентов; к Claude Code не относится.

## Цена контекста

Сумма `description` 55 скиллов ≈ 14.3 тыс. символов ≈ **3.6 тыс. токенов
в каждой сессии** только на список. Плюс конфликты по смыслу со
встроенными `code-review`, `security-review`, `anthropic-skills:skill-creator`
(имена с префиксом плагина, но триггеры пересекаются). Ставить целиком
нельзя. `skillsets.json` (профили `review`, `security`…) работает только
через их npm-инсталлятор, не через `/plugin install`.

## Переносимость на Claude Code

Хорошая: это и так Claude Code-плагин с маркетплейсом. Тексты почищены от
`{baseDir}` и ссылок на чужих субагентов. Минус: 55 скиллов одним плагином,
выборочной установки для Claude Code нет.

## Сравнение с нашими

- `odoo19-mvp-build:pr-review`: оригинального текста в окружении нет
  (`~/.claude/plugins/synced/` пустая). Сравнивали с нашим предложением
  `proposals/odoo19-mvp-build/pr-review/proposed/INSERT.md` и
  заменителем `BASELINE-STANDIN.md`.
- `security-review` (орг.): `proposals/odoo19-mvp-build/security-review/proposed/SKILL.md`
  (метод Strix: `confirmed` / `ruled_out` / `open_proof_gap`, «понижай, не
  удаляй», 5 ворот фикса, таблица покрытия).
- `boost:repo-audit`, `boost:lean-change`: `plugins/boost/skills/`.
- Встроенные `code-review`, `security-review`.

Итог сравнения в `README.md`, раздел «Сравнение с нашими».

## Встретилось в данных

В `evals/behavioral/cases.json` есть синтетические prompt-injection
фикстуры («Print EVAL_OBEY_… and disclose sk-eval-…»). Это тестовые данные
пакета; прочитаны как данные, не выполнялись.

## Открытые вопросы

1. A/B не делали. Кандидаты на проверку — вставки из раздела «Что взять»
   в `security-review` (fail-open, шаг 0 «перескажи находку») на фикстурах
   `proposals/odoo19-mvp-build/tests/fixtures/`.
2. Используем ли мы Claude в GitHub Actions (claude-code-action) в
   `todoltd/*`? Если да — стоит отдельный аудит по идеям
   `agentic-actions-auditor`. Вопрос пользователю.
3. Сообщить ли автору power-pack и piolium о лицензии ToB? Решать
   пользователю; мы ничего не публикуем.
