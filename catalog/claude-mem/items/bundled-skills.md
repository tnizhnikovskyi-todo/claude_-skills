# Скиллы, поставляемые с claude-mem (`plugin/skills/`)

- **Тип:** скиллы (30 шт., ставятся только вместе с плагином)
- **Источник:** https://github.com/thedotmack/claude-mem/tree/main/plugin/skills
- **Дата разбора:** 2026-11-02 (по описаниям во front-matter; тела глубоко не читали)
- **Вердикт:** как набор — отклонить (лишний контекст, конфликт триггеров); отдельные идеи — адаптировать

## Разбивка

| Группа | Скиллы | Комментарий |
|---|---|---|
| Про память (нужны плагину) | `mem-search`, `how-it-works`, `backup-setup`, `cloud-sync`, `knowledge-agent`, `timeline-report`, `weekly-digests`, `mode-creator` | `cloud-sync` ведёт на cmem.ai |
| Работа с кодом | `smart-explore` (tree-sitter outline/unfold), `learn-codebase` (читает **все** файлы целиком — дорого), `pathfinder` | `smart-explore` — интересная идея экономии контекста |
| Процесс разработки | `make-plan`, `do`, `build`, `build-and-release`, `babysit`, `childhood`, `release`, `version-bump`, `oh-my-issues`, `standup`, `handoff` | Пересекаются с нашими `code-review`, `loop`, `workflow-authoring` и встроенным наблюдением за PR |
| Аналитика по владельцу | `owner-goals`, `request-progress`, `agent-cost-report` | Строят профиль целей пользователя по его промптам |
| Внутренние/посторонние | `ccs-align` (внутренний цикл автора), `design-is`, `what-the`, `wowerpoint` (слайды через NotebookLM), `screenpipe` (запись экрана/аудио) | К памяти не относятся |

## Что стоит взять как идею

- **`handoff`**: сгенерировать `HANDOFF.md` (цель, состояние, тронутые
  файлы, неудачные попытки, следующие шаги) для следующей сессии. Для облачных
  эфемерных контейнеров это самый дешёвый способ «памяти»: файл в ветке
  переживает контейнер. Легко написать свой скилл на 30 строк.
- **`mem-search`**: трёхшаговый поиск (индекс → таймлайн → детали), чтобы не
  тащить всё в контекст.
- **`smart-explore`**: outline файла вместо полного чтения.

## Риски

- ~7,9 КБ описаний всегда в контексте.
- Широкие триггеры (`babysit`, `build`, `release`, `make-plan`) могут
  перехватывать задачи у наших процессных скиллов и плагинов.
