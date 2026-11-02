# Источники и лицензии

Скилл собран из идей трёх разобранных репозиториев. Код и текст не
копировались дословно: формулировки, карточки, шаблоны и якоря рубрики
написаны заново. Совпадают только идеи и веса рубрики.

| Идея | Источник | Лицензия | Разбор |
|---|---|---|---|
| Проверка субагентом со свежим контекстом, которому не передаются выводы автора (ARTIFACT + CONTRACT); максимум 3 цикла; сигнал «doubt theater» | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills/tree/main/skills/doubt-driven-development) `skills/doubt-driven-development`, v0.6.15 / `301b02b` | MIT | `catalog/agent-skills/items/doubt-driven-development.md` |
| Карточки стратегий, атака → защита → судья по взвешенной рубрике (30/25/20/15/10, правило fatal), финальное слепое сравнение с исходным ответом | [Jakeschincariol/arena-skill](https://github.com/Jakeschincariol/arena-skill) `df07b8e` | MIT | `catalog/arena-skill/README.md` |
| Закрытие кандидата: confirmed / ruled_out (с названным контролем и местом) / open_proof_gap; список того, что не доказывает безопасность; «понижай, не удаляй»; не схлопывать места | [usestrix/strix](https://github.com/usestrix/strix/tree/main/strix/skills/analysis) `counterevidence.md`, `severity_calibration.md`, `6b7ae2e` | Apache-2.0 | `catalog/strix/items/analysis-methodology.md` |

Отличия от оригиналов: арена сокращена со 100 агентов и 7 раундов до 2–4
критиков, 1 судьи и 1–2 раундов, без отбора на выбывание и без
`bracket.py`; субагенты технически только читают (агент
`independent-check-reviewer` с инструментами Read, Glob, Grep); запуск
только по явной просьбе; без внешних CLI и сторонних моделей.
