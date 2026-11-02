# Strix: knowledge packs по уязвимостям и технологиям

- **Тип:** справочные markdown-файлы, подгружаемые агентам
- **Источник:** `strix/skills/{vulnerabilities,frameworks,technologies,protocols,cloud,tooling,custom,reconnaissance}`
- **Версия / коммит:** `6b7ae2e`
- **Дата разбора:** 2026-11-02
- **Вердикт:** брать выборочно как справку (не ставить целиком)

## Что внутри

~70 файлов по 60–560 строк, всего ~13 тыс. строк:

- **vulnerabilities (29):** idor, business_logic, mass_assignment,
  broken_function_level_authorization, race_conditions, sql_injection,
  nosql_injection, ssti, xss, csrf, ssrf, xxe, rce, path_traversal,
  insecure_file_uploads, insecure_deserialization, authentication_jwt,
  open_redirect, header_injection, http_request_smuggling,
  information_disclosure, prototype_pollution, subdomain_takeover,
  weak_password_detection, llm_prompt_injection, agentic_system_security,
  semantic_confusion, argument_injection, browser_security.
- **frameworks:** django, fastapi, nestjs, nextjs (Odoo нет).
- **technologies:** supabase, firebase, auth0, grafana/prometheus,
  active directory, electron, llm_applications.
- **protocols:** oauth, graphql. **cloud:** aws, gcp, azure, kubernetes.
- **tooling:** nmap, nuclei, sqlmap, ffuf, semgrep, httpx, katana, hurl,
  hypothesis, agent_browser и др.
- **custom:** source_aware_sast, dependency_cve_scanning, api_spec_testing,
  npx_confusion.

## Что полезно нам

Для Odoo-модулей самые релевантные: `idor`, `business_logic`,
`mass_assignment` (ср. `write()`/`create()` с полями из request),
`broken_function_level_authorization` (контроллеры), `race_conditions`
(двойное списание/подтверждение), `insecure_file_uploads`, `ssti`
(QWeb/`safe_eval`), `sql_injection`, `csrf`. Из технологий —
`llm_applications` / `llm_prompt_injection` / `agentic_system_security`,
если будем ревьюить свои AI-интеграции и MCP-серверы.

Способ использования: не грузить в контекст постоянно, а положить 3–5
ужатых выжимок как `references/` будущего Odoo-security скилла,
подгружаемых по требованию.

## Оценка

| Критерий | Балл (0–3) | Комментарий |
|---|---|---|
| Прирост | 1 | Модель в целом знает эти классы; ценность в чек-листах и «семействах» |
| Частота | 2 | Несколько классов актуальны в каждом ревью |
| Надёжность | 2 | Качественные тексты, не испытаны |
| Стоимость контекста | 1 | Целиком очень тяжело; только выборочно |
| Безопасность | 3 | Текст; payload-ы атакующие, но это справка |
| Поддержка | 3 | Активно |
| **Итого** | **12/18** | |
