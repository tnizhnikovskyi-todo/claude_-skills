# Strix: рабочий журнал

## 2026-11-02 — первичный разбор

**Что смотрели** (клон в scratchpad, вне репозитория, ничего не запускали):

- `README.md`, `AGENTS.md`, `pyproject.toml`, `LICENSE` (Apache-2.0),
  `benchmarks/README.md`, git-лог (активность, авторы, теги до v1.7.0).
- `strix/agents/prompts/system_prompt.jinja` целиком (~540 строк).
- `strix/skills/analysis/{counterevidence,severity_calibration,source_aware_discovery,fix_verification}.md`,
  `scan_modes/{diff,quick}.md`, `coordination/source_aware_whitebox.md` — целиком.
- Список остальных knowledge packs (по именам и размерам).
- `skills/*/SKILL.md` (9 consumer-скиллов): два прочитаны целиком
  (`penetration-testing-with-strix`, `find-security-vulnerabilities-in-code`),
  остальные по `AGENTS.md`.
- Безопасность: `strix/telemetry/*`, `config/settings.py` (телеметрия
  `default=True`), `tools/web_search` (Perplexity / Exa),
  `runtime/docker_client.py` (cap_add), `containers/Dockerfile`,
  все внешние хосты в Python-коде (grep).
- `tools/threat_model` (обязательные разделы), `tools/coverage` (исходы),
  `tools/reporting` (обязательные поля counterevidence и т.п.).

**Что проверили / установили:**

- Активность: 313 коммитов с 2026-08-01, ~125 в октябре; основные авторы
  Ahmed Allam / 0xallam; есть devin-бот и dependabot.
- Внешние хосты: posthog, scarf (телеметрия), perplexity/exa (поиск),
  app.strix.ai (облако), auth.openai.com/chatgpt.com (Codex OAuth),
  api.getpostman.com, pypi/npm (проверка версий), api.github.com.
- Контейнер: Kali, NOPASSWD sudo, `NET_ADMIN`/`NET_RAW`, `SYS_ADMIN`
  при FUSE-монтированиях, порты биндятся на 127.0.0.1.
- В системном промпте есть разделы `AUTHORIZATION STATUS` и
  `REFUSAL AVOIDANCE` — модель настраивают не сомневаться в авторизации.
- Нет Odoo-специфики (фреймворки: Django, FastAPI, NestJS, Next.js).
- Docker в нашем контейнере есть (`/usr/bin/docker`), но не запускали.

**Сравнение с тем, что есть** (`inventory/current.md`):

| | встроенный `security-review` | `odoo19-mvp-build:security-review` | Strix |
|---|---|---|---|
| Вход | diff ветки | diff `td.*` модуля | код, git, URL, домен, OpenAPI |
| Анализ | статический, один проход | статика + Odoo-чеклист (ACL, record rules, `sudo()`, SQL, маршруты, секреты) | статика (semgrep, ast-grep, gitleaks, trivy) + **динамика** (прокси, браузер, PoC) |
| Знание Odoo | нет | **да** | нет |
| Дисциплина закрытия кандидата | нет явной | нет явной | `confirmed` / `ruled_out` с названным контролем / `open_proof_gap` |
| Калибровка severity | общая | APPROVE / REQUEST CHANGES / BLOCK | рубрикатор + чек-лист high/critical + CVSS с привязкой к доказательствам |
| Что покрыто | не сообщается | не сообщается | coverage ledger, включая «чисто» |
| Проверка фикса | нет | «concrete fixes» без ворот | 5 ворот, право не предлагать фикс |
| Стоимость / время | секунды–минуты, в контексте | минуты | 10 мин – часы, $5–30+, вне контекста |
| Риски | нет | нет | Kali-контейнер, телеметрия, код к LLM-провайдеру |

**Вывод:** сверх наших скиллов Strix умеет (1) динамически доказывать,
(2) системно закрывать кандидатов и сообщать покрытие, (3) калибровать
severity и проверять фиксы. Пункты 2–3 переносимы текстом без запуска
Strix. Пункт 1 — только запуском инструмента.

## Открытые вопросы

1. Нужен ли нам вообще динамический пентест стендов Odoo? Если да —
   разрешить пробный прогон Strix (quick, $5, свой стенд, телеметрия off)?
2. Куда встраивать методологию: правка `odoo19-mvp-build:security-review`
   (плагин организации) или отдельный reference-файл, который подгружается
   из обоих ревью?
3. A/B-тест: есть ли 2–3 исторических PR `td.*` с известной проблемой
   доступа, чтобы сравнить ревью с методологией и без?
4. Делать ли черновик ужатой методологии (~150 строк, по-русски/англ.)
   прямо в этой папке?
