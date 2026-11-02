# Caveman: рабочий журнал

## 2026-11-02, первичный разбор

**Клон:** `git clone https://github.com/JuliusBrussee/caveman` в scratchpad,
коммит `2e068f73` (2026-11-01), теги `v4.0.1`, `bin-v4.0.2`. 1796 файлов,
1888 коммитов с 2026-04-04, из них 1040 в октябре 2026. Ничего не запускалось.

**Что прочитано:**
- `README.md`, `LICENSING.md` (Apache-2.0 на весь репо с 3.0.0; до этого
  MIT + BSL для рантайма; облако закрытое).
- `skills/caveman/SKILL.md`, `skills/ultracave/SKILL.md`, `skills/cavecrew/SKILL.md`.
- `.claude-plugin/plugin.json`, `marketplace.json`: 4 хука на Node.
- `src/hooks/*.js` (grep на сеть и запуск процессов: сети нет,
  `execFileSync` только для локального stats-скрипта).
- `docs/HONEST-NUMBERS.md`, `docs/technical/product-model.md`.
- `shrink/README.md`, начало `skills/caveman-compress/scripts/compress.py`
  (вызывает `claude` CLI или Anthropic API, модель по умолчанию
  `claude-sonnet-4-5`).
- `packages/cli/src/index.ts`: grep по `ANTHROPIC_BASE_URL` и телеметрии
  (`TELEMETRY_URL` на `*.supabase.co/functions/v1/cli-telemetry`).

**Что не проверено:**
- Код Engine/прокси на Go (сотни файлов) не читался построчно.
- Внешние ссылки (Adobe arXiv, JetBrains, Elastic) не открывались.
- A/B не проводился.

## Ключевые наблюдения

- Сам автор признаёт, что стилевой скилл почти не влияет на счёт в агентных
  сессиях (output ≈ 0.3% токенов) и может быть в минусе на коротких Q&A
  (issue #145) и в Cursor (#550: 4.3M против 1M токенов).
- Против простой инструкции «Answer concisely.» `caveman` даёт всего −3%
  output по медиане; `ultracave` −35%.
- Проект эволюционировал из скилла в продукт с облаком и монетизацией
  (Caveman Cloud, Auto). Установка через CLI ставит гораздо больше, чем скилл.
- Текст правил `caveman` хорош как стилевой гайд и полезен сам по себе.

## Пересечения с rtk

Ветка `analysis/rtk` на момент разбора ещё не запушена (`git fetch` не нашёл),
поэтому сравнение по известному из `catalog/omniroute/items/compression.md`
и документации caveman:

| | caveman | rtk |
|---|---|---|
| Что сжимает | в первую очередь **output** (стиль ответа); в 4.0 также input через прокси | **input**: вывод shell-команд перед попаданием в контекст |
| Как встраивается | скилл + хуки `SessionStart`/`UserPromptSubmit`; прокси через `ANTHROPIC_BASE_URL` | хук/обёртка над командами (по omniroute) |
| Пересечение | `caveman shrink -- <cmd>` прямо заявлен как «RTK parity» в `docs/technical/agent-profile-registry.md` | основная функция |
| Риск | стиль: низкий; прокси: высокий | уточнить в разборе rtk |

Вывод: по сжатию **вывода команд** caveman догоняет rtk, а не наоборот. Если
нужна экономия input на выводе команд, первоисточник там rtk. Caveman ценен
другим: стилевыми правилами ответа и контрактом сжатого отчёта субагентов.
Главная сессия: сверить с `catalog/rtk/summary.md`, когда ветка появится.

## Открытые вопросы

1. Провести A/B на нашей реальной задаче: обычный ответ vs «be concise» vs
   своя русская версия правил (~30 строк). Мерить читаемость и токены.
2. A/B контракта отчёта субагента (`cavecrew`-стиль) на задаче поиска по коду.
3. Нужно ли глубже читать Engine/CCR как образец «сжатие с восстановлением»?
