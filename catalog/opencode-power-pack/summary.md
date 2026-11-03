# opencode-power-pack — итог

- **Что это:** сборник 55 чужих скиллов под Claude Code / Codex / OpenCode / Pi
  (`waybarrios/opencode-power-pack@c3328ad`, v0.6.0). Свой скилл один
  (`humanizer`); 25 из Hugging Face, 11 из Anthropic, 14 скиллов
  безопасности через `vigolium/piolium`, по сути из `trailofbits/skills`.
- **Вердикт:** плагин отклонить (≈3.6 тыс. токенов описаний в каждой сессии,
  дубли встроенных `code-review`/`security-review`, нам нужны 3–4 из 55).
  Адаптировать 4 идеи. Итог 8/18.
- **Лицензия:** 12 скиллов безопасности взяты у Trail of
  Bits (CC BY-SA 4.0), 5 из них почти дословно, а помечены MIT. Берём из них только идеи своими
  словами; за текстом идти в `trailofbits/skills@711af09`.
- **Что взять (подробно в `README.md` → «Что взять»):**
  1. `insecure-defaults` → `security-review` + `repo-audit`: fail-open vs
     fail-secure, Odoo-таблица (`get_param(..., default)`, `verify=False`,
     `auth='public'`, секретное поле без `groups=`). Самое новое для нас.
  2. `fp-check` → `security-review`: шаг 0 «перескажи находку», ворота
     достижимости и окружения, цепочки из `ruled_out`. Ядро уже есть (Strix).
  3. `differential-review` → `pr-review`: риск по содержанию, `git blame`
     удалённого защитного кода, переопределения через `_inherit`.
  4. `supply-chain-risk-auditor` → `criteria.md`: 6 признаков риска вместо
     одной шкалы «Поддержка» + признак «цепочка лицензий».
- **Отложено:** `agentic-actions-auditor` (9 векторов атаки на CI с ИИ) —
  если у нас есть workflow с `claude-code-action`.
- **A/B не делали;** внешний код не запускали. Кандидат на A/B: п. 1–2 на
  фикстурах `proposals/odoo19-mvp-build/tests/fixtures/`.
