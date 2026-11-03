# careful / freeze / guard

- **Тип:** скиллы с хуками `PreToolUse` во frontmatter + bash-скрипты
- **Источник:** `careful/SKILL.md@7caca33`, `careful/bin/check-careful.sh` (424 строки), `freeze/SKILL.md`, `guard/SKILL.md`
- **Лицензия:** MIT
- **Вердикт:** отклонить; записать приём «хуки в frontmatter скилла»

## Что делает

`/careful` на время сессии включает хук на Bash/PowerShell: `rm -rf`,
`DROP`/`TRUNCATE`, `git push -f`, `git reset --hard`, `git checkout .`,
`kubectl delete`, `docker system prune` → `permissionDecision: ask`;
`rm -r /` и force-push в ветку по умолчанию → deny. Исключения:
`node_modules`, `dist`, `__pycache__` и т.п. `/freeze <dir>` запрещает
Edit/Write вне каталога; `/guard` = оба. `investigate` ставит `freeze`
сам на каталог модуля.

## Почему отклоняем

- В Claude Code уже есть правила прав (`deny`/`ask` в `settings.json`) и
  классификатор auto mode, который в этой же сессии отказывал в
  рискованных действиях. Сам `careful` честно пишет, что строковое
  сопоставление — «best-effort», и для жёсткого стопа советует правила
  прав.
- Скрипты пишут аналитику в `~/.gstack/analytics/`.
- Пути зашиты на `~/.claude/skills/gstack/…`.

## Что ценно (идея)

**Хуки в frontmatter `SKILL.md` активны только пока скилл вызван.** Это
решает наш минус «always-on хуки» (`criteria.md`): барьер (принцип
«второе нарушение лечится барьером») можно повесить на один скилл, а не
на всю сессию. Пример для нас: `lean-change` или будущий
`debug-root-cause` запирают правки в каталоге модуля Odoo. Перед
использованием проверить, поддерживает ли наш маркетплейс/версия Claude
Code `hooks` во frontmatter скиллов плагина.

## Оценка

| Критерий | Балл | Комментарий |
|---|---|---|
| Прирост | 1 | Дублирует права и auto mode |
| Частота | 1 | — |
| Надёжность | 2 | Best-effort по строкам |
| Стоимость контекста | 3 | Короткие скиллы |
| Безопасность | 2 | Скрипты прочитаны частично, пишут в `~/.gstack` |
| Поддержка | 3 | Активно |
| **Итого** | **12/18** | |
