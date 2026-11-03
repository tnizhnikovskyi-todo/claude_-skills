# ECC — рабочий журнал

## 2026-11-03

### Что склонировали
- `affaan-m/ECC`, `main` @ `b38be6a7f6350964d59328b52f0624e1d1d552d1`
  (2026-10-29), версия 2.2.3. Клон в scratchpad, вне репо. Ничего не
  запускали (скрипты, `install.sh`, хуки, MCP, `npx`).
- Для проверки активности догрузили историю без блобов
  (`git fetch --filter=blob:none --depth=10000`): 4321 коммит.

### Популярность: накрутка или нет
- Поиск GitHub: 296 302 ★, 43 824 форка, создан 2026-01-18, последний пуш
  2026-11-02, 216 открытых issues/PR. Всего issues 940, слитых PR 1345.
- История: 4321 коммит, 517 разных авторов; помесячно 78 (янв) → 569
  (мар) → 134 (июл) → 955 (окт). Основные: Affaan Mustafa 1636+141,
  `haelyra` 665 (в октябре 64 из 100 последних коммитов), далее десятки
  внешних авторов с 30–100 коммитами.
- Issues содержательные (баги хуков на Windows, обход gateguard через
  `.claude/settings*.json`, пропуски редактирования секретов), но много и
  мусорных «[Copilot]» без текста — признак широкой случайной аудитории.
- Форки/звёзды ≈ 15% — для накрутки нетипично (у купленных звёзд форков
  почти нет). Звездочётов через API проверить не смогли (доступ к API
  репозитория у сессии закрыт, работает только поиск).
- Вывод: активность настоящая, проект живой; 296 тыс. ★ за 10 месяцев —
  вирусная популярность (хайп вокруг «полного набора для Claude Code»),
  а не мерило качества. Звёзды как сигнал пользы игнорируем.

### Лицензия
- Корневой `LICENSE`: MIT, © 2026 Affaan Mustafa.
- Внутри есть файлы под другими лицензиями (frontmatter `license:`):
  CC-BY-SA-4.0 — `skills/osint-investigation` (свой `LICENSE.txt`);
  Apache-2.0 — 8 скиллов логистики/производства
  (`customs-trade-compliance`, `returns-reverse-logistics`,
  `carrier-relationship-management`, `energy-procurement`,
  `production-scheduling`, `logistics-exception-management`,
  `quality-nonconformance`, `inventory-demand-planning`);
  `skills/context-and-decisions/LICENSE` — MIT, © Matt Pocock.
- `gateguard` — `origin: community`, код ссылается на
  `github.com/zunoworks/gateguard`; `santa-method` — автор Ronald Skelton
  (RapportScore.ai). Для них лицензия = MIT корня, но атрибуцию автору
  сохраняем.
