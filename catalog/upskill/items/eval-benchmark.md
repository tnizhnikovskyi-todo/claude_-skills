# upskill eval / benchmark / runs

- **Тип:** команды CLI
- **Источник:** `src/upskill/evaluate.py`, `src/upskill/verifiers.py`, `src/upskill/models.py:436-470`, `README.md` @ `eec8ab4`
- **Лицензия:** Apache-2.0
- **Вердикт:** отклонить как инструмент; взять правило принятия с токенами (идея 3) и матрицу «скилл × модель» (идея 4)

## Что делает

- `eval <скилл>`: кейсы (JSON/YAML или сгенерированные) прогоняются
  «with-skill» и «baseline», параллельно (`max_parallel` 5). Метрики:
  доля успешных кейсов, токены, ходы; `skill_lift`, `token_savings`,
  `is_beneficial`.
- `eval -m haiku -m sonnet --runs 5` / `benchmark`: матрица моделей и
  повторов; baseline в этом режиме выключен.
- `runs`: бары «baseline → with skill» по моделям, матрица
  «скилл × модель», экспорт CSV. Логи: `runs/<batch>/run_N/run_result.json`.

## Проверка результата

Верификаторы: `contains` (подстрока, регистр не важен), `file_exists`,
`file_contains`, `command` (`shell=True`, таймаут 60 с, вывод до 1200
символов), legacy `validator`. Кейс проходит, только если прошли все.
LLM-судьи нет.

## Сильное

- Токены — полноправная метрика рядом с качеством:
  `is_beneficial = lift > 0.05 or (lift >= 0 and token_savings > 0.2)`.
- Матрица «скилл × модель» отвечает на вопрос «на какой модели скилл
  нужен», а не только «помогает ли он».
- Артефакты каждого кейса (`test_result.json`) сохраняются, итог можно
  пересобрать без перепрогона.

## Слабое

- Меряет в fast-agent: скилл подложен через `--skills-dir`, триггер по
  `description` в Claude Code, хуки и инструменты не проверяются.
- Обе руки получают системный промпт «You are an evaluator of skills…
  return a score».
- По умолчанию 1 прогон, без дисперсии; в benchmark нет baseline.
- Подстрочные грейдеры, нет негативных кейсов.

## Сравнение

`claude plugin eval` (`plugins/boost/evals/README.md`) делает ту же
A/B-схему точнее. Не хватает у нас: токенов в правиле принятия
(сейчас «без положительной разницы не включаем», цена учитывается
словами) и прогона на второй модели.
