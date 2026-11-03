# sh-kb-* (15 баз знаний) и их самообновление в CI

- **Источник:** `plugins/security-harness/skills/sh-kb-*/SKILL.md@68748d5`,
  `.github/workflows/update-knowledge-base.yml@68748d5`, `.github/workflows/kb-review-and-merge.yml@68748d5`,
  `.github/kb-update/*@68748d5`
- **Вердикт:** отклонить (KB); идея двухагентного гейта для автообновлений — на заметку

## Что это

15 скиллов по 3–7 КБ, единый шаблон: когда искать → источники и синки → рецепт →
PoC → фильтры ложных срабатываний → CWE/OWASP → chaining → mitigation. Грузятся только
охотником своего класса (дёшево по контексту). Примеры и синки — Express, Django, Flask,
Spring, Rails, Laravel. Odoo не упоминается.

Раз в два дня агент в GitHub Actions читает allowlist доменов (OWASP, PortSwigger, CWE,
NIST, MDN, `github.com`, `hackerone.com`) и правит KB, без shell и без push. Отдельный
агент-ревьюер без веба и shell ищет в диффе инъекции промптов, утечки, выход за scope.
Fail-closed; при APPROVE PR сливается автоматически (через auto-merge GitHub, если включён).

## Оценка

- Как знания для нас: слабо. Наш `security-review` уже содержит Odoo-эквиваленты
  (ACL, `ir.rule`, `sudo()`, `cr.execute`/`SQL`, `Markup`, `auth=`, CSRF). Общие
  веб-классы (SSRF, XXE, deserialization) у нас встречаются редко.
- Как риск: установленный плагин тянет `main`, в который агент сам вливает текст из веба.
  Промпты меняются без нашего ревью. Если ставить — только с пином коммита.
- Интересная идея для нашего цикла улучшения скиллов (`observations/` в `synthesis.md`,
  п. 8): автоправки текста скилла пропускать через отдельного ревьюера с другими
  инструментами (без веба) и fail-closed. Только идея, своими словами.
