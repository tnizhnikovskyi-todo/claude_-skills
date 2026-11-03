# opencode-power-pack — итог

- **Что это:** сборник 55 чужих скиллов под Claude Code / Codex / OpenCode / Pi
  (`waybarrios/opencode-power-pack@c3328ad`, v0.6.0). Свой скилл один
  (`humanizer`); 25 из Hugging Face, 11 из Anthropic, 14 скиллов
  безопасности через `vigolium/piolium`, по сути из `trailofbits/skills`.
- **Вердикт:** плагин отклонить (≈3.6 тыс. токенов описаний в каждой сессии,
  дубли встроенных `code-review`/`security-review`, нам нужны 3–4 из 55).
  Итог 8/18. Адаптировать 5 небольших вставок по 1–3 строки.
- **Лицензия:** 12 скиллов безопасности взяты у Trail of Bits (CC BY-SA 4.0),
  5 из них почти дословно, а помечены MIT. Берём только идеи своими словами;
  за текстом идти в `trailofbits/skills@711af09`.
- **Сверка с действующими текстами** `odoo19-mvp-build`
  (`todoltd/claude-methodology-marketplace@7acde05`, приватный, только
  чтение): наши вставки Strix/ponytail там уже есть. Поэтому прирост от
  power-pack небольшой.
- **Что взять (подробно в `README.md` → «Что взять»):**
  1. `security-review`, Dimension 6: `get_param(key, default='<секрет/URL>')`
     = как хардкод; TLS выключен по умолчанию (`insecure-defaults`).
  2. `security-review`: шаг 0 «перескажи находку», в конце цепочки из
     `ruled_out`/понижённых (`fp-check`).
  3. `pr-review`: риск файла по содержанию; переопределения изменённого
     метода через `_inherit` (`differential-review`).
  4. `pr-review`, раунд критиков: «упавший или частичный критик → Not checked,
     а не чисто» (`code-review`, Apache-2.0).
  5. `criteria.md`: 6 признаков риска к «Поддержке» + «цепочка лицензий»
     (`supply-chain-risk-auditor`).
- **Отложено:** `agentic-actions-auditor` (9 векторов атаки на CI с ИИ), если
  у нас есть workflow с `claude-code-action`.
- **A/B не делали;** внешний код не запускали.
