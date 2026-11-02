---
name: security-review
description: >
  Security audit of a custom Odoo `td.*` module before deploy — Track 1's security gate,
  run after `pr-review` APPROVE and before `track-convergence`. Audits access control
  (`ir.model.access`, record rules), `sudo()` use, SQL injection in raw queries, controller/route
  exposure, hardcoded secrets, and cross-record data access. Engine: the built-in `/security-review`
  on the diff PLUS an Odoo-specific checklist the generic scanner misses. Triggers on:
  "security review", "безпековий аудит", "перевір безпеку модуля", "security audit", "audit the
  module before deploy", "перевір права доступу", "is this module safe to deploy". NOT code-vs-spec
  review (that is pr-review) nor live-config review (config-review). Outputs APPROVE / REQUEST
  CHANGES / BLOCK per finding, with concrete fixes.
---

# Odoo Security-Review — gate before deploy

Structured security audit of a custom `td.*` module. The SDD chain has gates for
spec-compliance (`pr-review`) and configuration (`config-review`), but **no security
gate** — this skill is that gate. It runs on Track 1 **after `pr-review` APPROVE** and
**before `track-convergence`/deploy**; its APPROVE is required before custom code reaches
a shared instance or UAT.

Outputs a verdict (APPROVE / REQUEST CHANGES / BLOCK) with specific, per-finding fixes.

## Engine: built-in `/security-review` + Odoo layer
- **Step A — run `/security-review` on the diff.** It catches language-level issues
  (injection, unsafe deserialization, secrets, path traversal). Use it as the automated first pass.
- **Step B — apply the Odoo-specific checklist below.** The generic scanner does **not**
  understand Odoo's ACL/record-rule/`sudo()`/controller model — most real Odoo vulns live there.
  Steps A and B are both required; this skill's verdict combines them.

**Critic round: Risk/Security critics (optional, П20 layer):**
- Tool: `Agent`, run **in parallel** (one message) after Steps A+B. Give each the diff +
  SPEC.md + their lens + "find 🔴/🟡, do NOT edit, return concrete fixes, don't rely on my verdict":
  1. **Access-control critic** — ACL rows, record rules, group design, portal/public exposure.
  2. **Injection/secrets critic** — raw SQL, `eval`/`safe_eval`, controller input, hardcoded creds.
  3. **Odoo-19 expert** — that each control is the real v19 mechanism (no invented API), `sudo()` semantics.
- **Consolidate** under "Critic round (iter N)"; dedup, prioritize 🔴/🟡. **Iterations:** after fixes
  (by `code-dev`, with sign-off) re-run; stop at 0 🔴 or max **2 iterations**.
- Human-in-the-loop: critics read/propose — they do not edit. Unavailable → single pass (enhancement, not dependency).

**Knowledge Base connector (optional, when the KB MCP connector is available):**
- Tools: `list_projects` · `find_documents` · `search_knowledge_base(query, project_ids)` · `get_documents` · `get_document_parts`.
- Rules: always scope `project_ids`; never copy sensitive data (client names, amounts, rates, креди) from other scopes into deliverables; the KB holds documents/transcripts only — NO code; connector unavailable / no hits → proceed without it (enhancement, not dependency).

## ToDo — еталон і межі
- This gate checks **security**, not spec-compliance (`pr-review`) or live config (`config-review`).
- Scope = the custom `td.*` module diff. Standard Odoo core is assumed audited; flag only where
  custom code weakens or bypasses core protections.
- AC ids are canonical `AC-01`. Where a security finding maps to an access-control AC, cite it.

## Inputs required
- Diff or changed files of the `td.*` module (models, security CSV/XML, controllers, views, data).
- `SPEC.md` (for the intended access model — who may do what).
- Target Odoo version + edition (Community/Enterprise).
- `pr-review` verdict (this gate runs after pr-review APPROVE).

## Review dimensions

Run all six. Each produces a verdict and a list of findings.

---

### Dimension 1 — Access control: `ir.model.access` (BLOCK if missing/over-broad)

> 🔎 **KB:** `search_knowledge_base("ir.model.access права доступу групи", project_ids=[analogs])` — how access was scoped on comparable td.* models (calibrates "who should have what").

- [ ] **Every new `td.*` model has at least one `ir.model.access.csv` row** — a model with no ACL row is either inaccessible or (worse) silently world-readable depending on context. Missing ACL on a user-facing model → BLOCK.
- [ ] ACL rows grant the **minimum** needed (no blanket `perm_write=1, perm_unlink=1` to a broad group without reason).
- [ ] No model is granted to `base.group_public` / `base.group_portal` unless the SPEC explicitly requires public/portal access — and then read-only unless justified.
- [ ] Group is a real group that exists in the manifest's `depends` (not an invented `td.group_*` with no definition).

### Dimension 2 — Record rules & cross-record access (BLOCK if data leaks across tenants/owners)

- [ ] Models with `company_id` have a **multi-company record rule** (`global=True`, domain `['|',('company_id','=',False),('company_id','in',company_ids)]`).
- [ ] Ownership-scoped data (a user should see only their own records) has a record rule enforcing it — not just a UI domain (UI domains are not security).
- [ ] No record rule uses an **over-permissive** domain (`[(1,'=',1)]` on a restricted group) that nullifies the intended restriction.
- [ ] Portal/public-exposed models have a record rule limiting rows to the authenticated partner.

### Dimension 3 — `sudo()` audit (BLOCK on privilege escalation; else REQUEST CHANGES)

> 🔎 **KB:** `search_knowledge_base("sudo обґрунтування bypass прав", project_ids=[analogs])` — precedents for when sudo() was accepted vs flagged.

- [ ] **Every `sudo()` has an explanatory comment** justifying why elevation is safe here.
- [ ] No `sudo()` runs a **user-controlled domain/search** (lets a user read arbitrary records) — that is privilege escalation → BLOCK.
- [ ] No `sudo()` on a `write`/`unlink`/`create` driven by unvalidated user input.
- [ ] Controllers do not `sudo()` to return data the caller's own rights would not allow.

### Dimension 4 — Injection & unsafe evaluation (BLOCK)

- [ ] **No raw SQL with string interpolation/f-strings** in `self.env.cr.execute(...)` — must use parameterized `%s` + params tuple. Interpolated user input → SQL injection → BLOCK.
- [ ] No `eval()` on user input; `safe_eval` only with a locked-down context, never on request data.
- [ ] No domain/order/field name built from raw `request`/`kwargs` without an allow-list.
- [ ] No unsafe deserialization (`pickle`/`yaml.load`) of external data.

### Dimension 5 — Controllers & routes (BLOCK on unauth data exposure; else REQUEST CHANGES)

> 🔎 **KB:** `search_knowledge_base("http.route auth controller контролер", project_ids=[analogs])` — real controller patterns from prior td.* modules.

- [ ] Every `@http.route` declares an explicit `auth=` — `'user'` by default; `'public'`/`'none'` only where intended and never returning private data.
- [ ] `type='json'` / state-changing routes have CSRF handled correctly (no `csrf=False` on a form POST without reason).
- [ ] Public routes do not leak other partners'/companies' records (check the query is scoped to the caller).
- [ ] No route returns stack traces / internal errors to the client; errors are caught and sanitized.

### Dimension 6 — Secrets, fields & irreversible ops (REQUEST CHANGES; BLOCK on hardcoded secret)

- [ ] **No hardcoded credentials, API keys, tokens, or passwords** in code/data XML → BLOCK. Use `ir.config_parameter` (or env), never commit secrets.
- [ ] Sensitive fields (salary, cost, personal data) carry `groups=` so they are not exposed to all users / in portal or public views.
- [ ] No secrets or PII written to `_logger` at info/debug level.
- [ ] Mass `write`/`unlink` and cron/server-actions running as superuser are scoped and reversible (or guarded) — flag wide-blast, irreversible operations.

---

## Review output format

```markdown
## Security Review: {module} (Odoo {version}/{edition})
Reviewing diff after: pr-review APPROVE
Engine: /security-review (Step A) + Odoo checklist (Step B)
Reviewer: AI (security-review skill)

---

### Verdict: {APPROVE | REQUEST CHANGES | BLOCK}

---

### 1. Access control (ir.model.access)
{PASS | BLOCK} — {findings, each file:line + fix, or "No issues."}

### 2. Record rules & cross-record access
{PASS | BLOCK} — {findings}

### 3. sudo() audit
{PASS | BLOCK | REQUEST CHANGES} — {findings}

### 4. Injection & unsafe evaluation
{PASS | BLOCK} — {findings}

### 5. Controllers & routes
{PASS | BLOCK | REQUEST CHANGES} — {findings}

### 6. Secrets, fields & irreversible ops
{PASS | BLOCK | REQUEST CHANGES} — {findings}

---

### Summary
{2–4 sentences: is the module safe to deploy, and what must be fixed first.}
```

## Verdict rules

| Condition | Verdict |
|-----------|---------|
| Any exploitable issue: SQL injection, missing ACL on user-facing model, `sudo()` privilege escalation, public route leaking data, hardcoded secret | BLOCK |
| No exploitable issue, but hardening gaps (uncommented `sudo()`, missing `groups=` on sensitive field, fragile controller) | REQUEST CHANGES |
| All six dimensions pass | APPROVE |

A BLOCK means the code track **cannot proceed to `track-convergence`/deploy** until fixed and
re-audited. APPROVE = security-clean → the code track is deploy-ready (together with `pr-review` APPROVE).

## Finding severity levels

| Prefix | Meaning | Required before deploy? |
|--------|---------|-------------------------|
| `VULN` | Exploitable (injection, data leak, escalation, secret) | Yes — BLOCK |
| `REQUIRED` | Hardening gap / missing control | Yes — REQUEST CHANGES |
| `WARNING` | Weak pattern, not directly exploitable | Recommended |
| `SUGGESTION` | Defense-in-depth idea | Optional |

## Guardrails
- **Read/analyze only** — never modify code here; fixes go to `code-dev` with BA/dev sign-off, then re-audit.
- Never run the module against production data to "test" an exploit; reason from the diff.
- Do not weaken the verdict to unblock a deadline — a BLOCK is a real vulnerability.

## Next step
Report: «Security: {APPROVE/REQUEST CHANGES/BLOCK}. VULN[N]/REQUIRED[M].» If APPROVE →
hand to `track-convergence` (deploy + master data). If REQUEST CHANGES/BLOCK → back to `code-dev`
for the listed fixes, then re-run this gate. Offer the choice via `AskUserQuestion`:
«Виправити зараз (code-dev)» / «Далі — track-convergence».

## DO / DO NOT
**DO**
- Run `/security-review` AND the Odoo checklist; combine both into one verdict.
- Cite each finding with a file:line and a concrete fix.
- BLOCK on any genuinely exploitable issue; keep `AC-NN` ids where access maps to an AC.

**DO NOT**
- Edit code, self-approve, or re-open the spec/config gates here.
- Treat the generic scanner's "clean" as sufficient — the Odoo ACL/sudo/controller layer is where the real risk is.
- Review spec-compliance (that is `pr-review`) or live configuration (that is `config-review`).
