# Атрибуция

Скилл `odoo-model-map` написан с нуля в этом репозитории. Чужой код не
копировался.

Откуда идеи:

- **serena** (https://github.com/oraios/serena, разбор `catalog/serena/`):
  «сначала оглавление (символы), потом метод» вместо чтения файлов целиком.
  Сам serena для Odoo отклонён: LSP не видит строковый `_inherit` и XML.
- **codebase-memory-mcp** (разбор `catalog/codebase-memory-mcp/`):
  вопросы «кто вызывает / что затронет изменение» (`trace_path`,
  `detect_changes`) как цель карты; здесь они решаются по строкам Odoo.
- **graphify** (разбор `catalog/graphify/`): метки достоверности связи;
  здесь их роль играет обязательная перепроверка попаданий и блок «Где не
  искал».
- **Принцип №28** из `starter-principles` проекта One Skill to Rule Them
  All (https://github.com/rebelytics/one-skill-to-rule-them-all, v3.8.1,
  `ba696b2`, лицензия CC BY 4.0, автор rebelytics): «отсутствие не
  доказывается суммирующим инструментом». Пересказан своими словами в
  разделе «Не нашёл ≠ нет».

Скрипт `scripts/odoo_map.py` и рецепты `references/grep-recipes.md` свои.
