# Источники идей

Скилл и процедура написаны с нуля; текст и скрипты источников не копировались.

| Идея | Источник | Лицензия | Разбор |
|---|---|---|---|
| Наблюдение как файл с YAML-frontmatter; структура Issue → Suggested improvement → Principle; статусы `open/actioned/declined/superseded/parked`; `siblings_checked`; правило «второе нарушение одного правила → барьер, а не новая формулировка»; еженедельное ревью с группировкой по скиллу, правкой копий и одобрением человеком | task-observer 3.8.1, автор rebelytics, https://github.com/rebelytics/one-skill-to-rule-them-all | CC BY 4.0 | `catalog/one-skill-to-rule-them-all/` |
| Триггер правила = предшествующая ситуация, тест точки решения, «детали сессии только через или», тест тавтологии; расширенные сигналы поправки; не выдумывать запрет без доказательства; слова пользователя ≠ текст инструментов; формат «путь успеха» (Применимо / Делать / Ограничения / Избегать / Проверка) | ReflexioAI/reflexio @ `49659eb` (движок claude-smart 0.3.17), `reflexio/server/prompt/prompt_bank/playbook_extraction_context/v4.6.1.prompt.md`, `playbook_should_generate/v3.0.0.prompt.md`, https://github.com/ReflexioAI/reflexio | Apache-2.0 | пересказ своими словами, изменено: сокращено, переведено, привязано к полям `rule`/`kind`/`evidence` | `catalog/claude-smart/` |
| `confidence` + доказательства у записи; в общее правило — только при повторе в 2+ проектах | affaan-m/ECC @ `b38be6a`, `skills/continuous-learning-v2/SKILL.md` («The Instinct Model», «Promotion»), https://github.com/affaan-m/ECC | MIT | идея | `catalog/ecc/` |
| `violation` против `gap` («есть ли правило, которое предотвратило бы ошибку»); слияние по отложенным кейсам; no-regression по каждому кейсу; ≤ 4 правки за ревью; правка описывает поведение, а не грейдер | microsoft/SkillOpt @ `bc0a392`, `skillopt/optimizer/skill_aware.py`, `skillopt_sleep/consolidate.py`, `gate.py`, `prompts.py`, `configs/_base_/default.yaml`, https://github.com/microsoft/SkillOpt | MIT | пересказ / идея | `catalog/skillopt/` |
| Парное A/B старой и новой версии в одной серии, нечётное число прогонов, ничья = не сливать (у источника ничья = оставить); лимит роста `SKILL.md` за правку (порог свой: ~15 строк / 20%); режим подтверждения `eval`/`manual`/`none`; исключение для барьера-линта на справочниках | alchaincyf/darwin-skill @ `8a8b662`, `SKILL.md`, `references/runtime-neutrality.md`, `references/skilllens-evidence.md`, https://github.com/alchaincyf/darwin-skill | MIT | пересказ своими словами | `catalog/darwin-skill/` |
| A/B только для изменённых скиллов (`git diff`); стоп по плато (< 0.05); антипаттерны «правка и оценка на одних кейсах», «строки грейдера в промпте правки»; leave-one-out раз в месяц | huggingface/upskill @ `eec8ab4`, `src/upskill/ci.py`, `cli.py`, `models.py`, `evaluate.py`, https://github.com/huggingface/upskill | Apache-2.0 | идея своими словами | `catalog/upskill/` |

Что сознательно не перенесено: always-on триггер на каждую сессию
(~11k токенов), чекпоинты записи по счётчику todo, скрипт-генератор id,
хуки активации, референсы на 8 600 строк, автономное применение правок
по расписанию. У нас наблюдение пишется только по поправке или просьбе,
а правку скилла всегда одобряет человек после A/B.
