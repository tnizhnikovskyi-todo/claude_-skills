# Рабочий журнал: requirement-engineer

## 2026-11-03

**Задача от главной сессии:** разобрать
https://github.com/MadurangaDev/requirement-engineer, проверить гипотезу
«активный инженер требований, который сам задаёт вопросы», сравнить с
`boost:interview-me` и `session-transcript-analyzer`.

### Что смотрели

- Клон в scratchpad, коммит `b728406` (HEAD), тег `beta` → `8cc6f85`.
  4 коммита, все 2026-07-04, один автор. 30 файлов, ~72 КБ, только `.md`
  и `LICENSE`.
- Прочитаны целиком: `SKILL.md`, все 9 `references/`, README, шаблоны
  `feature-requirements`, `acceptance-criteria`, `srs`, `definition-of-done`,
  пример `saas`. Остальные шаблоны и примеры — по размеру и заголовкам
  (0.2–4 КБ, без исполняемого).
- `grep` по `http|curl|fetch|bash|script|hook|telemetry` в `skill/`:
  ни одного вызова, только слова в тексте.
- Наше: `plugins/boost/skills/interview-me/SKILL.md` + `references/`,
  `reports/interview-source.md` (A/B +1.00 ×3), `reports/discovery-interview.md`,
  `catalog/agent-skills/items/interview-me.md`.
- `session-transcript-analyzer`: не в `~/.claude/plugins/synced/*/`
  (там пусто), а в `~/.claude/skills/synced/<id>/session-transcript-analyzer/SKILL.md`
  (21 КБ). `references/journal_template.md` в синхронизированной копии нет.
- `tr-usecases-acceptance`, `tr-review` — проверили, что «нещасливі шляхи»
  и Given/When/Then у нас уже есть.

### Что проверили и нашли

1. Гипотеза подтверждается наполовину: активная позиция есть, но вопросы
   «один или небольшая пачка», без догадки, без пересказа и «да»; по
   умолчанию выдаёт документ при неполном контексте.
2. Новое относительно нас: уверенность по 8 измерениям; сигналы «надо
   хотеть» (hedge, «как у X», общее против частного); 5 сигналов скрытых
   требований в рассказе; правило противоречий; EARS-граничные случаи
   (одновременный доступ, значение ровно на пороге).
3. Противоречит нашему опыту: «один сгруппированный вопрос лучше пяти»
   (narrative-elicitation.md) — у нас A/B за строго один вопрос.
4. Мелкие дефекты: ссылка на `ask_user_input_v0` (инструмент claude.ai),
   README ссылается на `CHANGELOG.md`, которого нет; дерево в README
   называется `requirements-engineer/`, а скилл `requirement-engineer`.
5. Атрибуция по цепочке: EARS-часть адаптирована из jasonkneen/kiro (MIT).

### Решения

- Вердикт: адаптировать частично, 10/18. Как есть не ставить.
- Главный перенос: 5 сигналов + правило противоречий в
  `session-transcript-analyzer` (через `proposals/`, плагин организации).
- Второй: измерения уверенности и сигналы «надо хотеть» в `interview-me`.

### Открытые вопросы к пользователю

- Разрешить A/B (3 кейса, описаны в `README.md` → «Проверка»)? Без него
  «адаптировать» остаётся гипотезой.
- Правка `session-transcript-analyzer` — это плагин организации; делать
  предложение в `proposals/odoo19-discovery/` (как задача 3.4) или ждать
  задачу в `roadmap.md`?
- Нужна ли EARS-формулировка в наших ТР, или Given/When/Then достаточно
  (склоняюсь: достаточно, брать только два граничных шаблона).
