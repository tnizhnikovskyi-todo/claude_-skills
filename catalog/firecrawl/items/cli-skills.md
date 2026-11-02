# firecrawl-cli и CLI-скиллы

- **Тип:** CLI + набор скиллов (`SKILL.md`) для Claude Code и других агентов
- **Источник:** https://github.com/firecrawl/cli (скиллы в `skills/`),
  каталог https://github.com/firecrawl/skills; build-скиллы в монорепо
  `firecrawl/skills/`
- **Версия / коммит:** npm `firecrawl-cli` 1.26.24, `a9a46fe` (2026-10-27)
- **Дата разбора:** 2026-11-02
- **Вердикт:** **отклонить как есть**; идеи (эскалация search → scrape →
  map → crawl → interact, вывод в файлы) можно взять в свой короткий скилл

## Что делает

Установка: `npx -y firecrawl-cli@latest init --all --browser` — ставит CLI
глобально, логинит через браузер, кладёт скиллы в `~/.agents/skills` и
линкует во все обнаруженные агенты (Claude Code, Codex, Cursor…).

13 CLI-скиллов (~81 КБ текста): `firecrawl` (зонтичный, 12 КБ),
`firecrawl-search` (14 КБ), `-scrape`, `-map`, `-crawl`, `-interact`,
`-agent`, `-parse`, `-download`, `-monitor`, `-alexandria`,
`-developer-index`, `-research-index`. Плюс отдельные семейства: build
(5 скиллов про интеграцию API в код) и workflows (SEO-аудит, лидогенерация,
ресёрч-брифы и т.п.).

Хорошая идея из `rules/security.md`: результаты пишутся в `.firecrawl/`
(в `.gitignore`), агент читает их частями через `grep`/`head`, а не тащит
страницу целиком в контекст — и меньше токенов, и меньше поверхность
prompt injection.

## Почему не как есть

- **Агрессивный триггер.** Описание зонтичного скилла: «Any live-web task …
  including ordinary web research … even when the task doesn't name
  Firecrawl». Будет перехватывать любые веб-задачи и тратить кредиты там,
  где хватило бы WebFetch.
- **`firecrawl setup defaults`** дописывает `WebSearch` и `WebFetch` в
  `permissions.deny` настроек Claude Code (`src/utils/web-defaults.ts`).
  Есть `--undo`, но включать нельзя: теряем бесплатный путь.
- **Глобальная установка и автообновления.** Скиллы ставятся во все
  найденные агенты сразу, CLI проверяет обновления каталога; явный
  `setup` перезаписывает локальные правки.
- `allowed-tools: Bash(firecrawl *)` — разумно узко, но требует
  глобальный npm-бинарник в среде.
- Пересекается с MCP-сервером: если подключён MCP, CLI-скиллы не нужны.

## Оценка

| Критерий | Балл | Комментарий |
|---|---|---|
| Прирост | 2 | Те же возможности, что MCP, через Bash |
| Частота | 2 | Как у MCP |
| Надёжность | 2 | Триггерится слишком широко |
| Стоимость контекста | 1 | 81 КБ скиллов, крупные `SKILL.md` по 9–14 КБ |
| Безопасность | 1 | Может отключить WebFetch/WebSearch, глобальные изменения в нескольких агентах |
| Поддержка | 3 | Активный репозиторий |
| **Итого** | **11** | |
