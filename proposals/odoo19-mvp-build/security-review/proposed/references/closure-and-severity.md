# Closure and severity — details for `security-review`

Adapted from Strix `strix/skills/analysis/counterevidence.md` and
`severity_calibration.md` (Apache-2.0, see `ATTRIBUTION.md`), mapped to Odoo 19.
Load when a candidate is hard to close or a VULN rating is borderline.

## What does NOT rule out a candidate (with Odoo examples)

| Excuse | Why it is not proof | Odoo 19 example |
|---|---|---|
| Generic trust in the framework | Escaping is per call and per context | `cr.execute("... ORDER BY %s" % order)`; `SQL(f"... {name}")` (f-string inside `SQL` is still interpolation); `SQL.identifier()` quotes identifiers, not values; `Markup(record.note)` / `fields.Html(sanitize=False)` / legacy `t-raw` render user HTML |
| UI-only restriction | RPC and controllers do not go through views | view `domain`, `invisible`, `readonly`, `groups=` on a `<field>`/`<button>` **in a view** (not on the field definition), menu restricted to a group |
| Control on a different path | Same sink, other entry point | button method checks state, but it is a public method (no `_` prefix) → callable via `/web/dataset/call_kw` by anyone with model access; same logic reached from a cron, server action, or `sudo()` caller |
| Control at the wrong time | Ordering bug | `rec = env['td.x'].sudo().browse(id); data = rec.read()` then `if rec.partner_id != user.partner_id: raise` — data already read/returned on another branch; `check_access` after `write` |
| Control that can fail open | Swallowed or optional | check inside `try/except Exception: pass`; allow-list empty by default; check skipped when `context.get('td_skip_check')` (context is caller-controlled over RPC) |
| Safe sibling | Each call site stands alone | `/my/td_orders` scoped by `partner_id`, `/my/td_orders/<int:id>/pdf` is not; do not merge them into one finding either |
| "A record rule exists" | Non-global rules of different groups are OR-ed; global rules AND-ed | a new `[(1,'=',1)]` rule for `td.group_viewer` that is implied by `base.group_user` opens all records to every internal user despite the restrictive rule for another group |
| Missing information | Absence of evidence | "no caller found" (RPC is a caller), "probably internal", "not in the menu", "cron only" → `open_proof_gap` |
| Difficulty | Not a control | "cannot run Odoo here" → record a proof gap, reason statically, move on |
| Configurable | What ships is what counts | "admin can add a rule", "parameter off by default" |
| Internal / admin-only | Lowers severity | internal user reading another company's data is still a finding |

## What DOES rule out a candidate

- A named control at a place, running on **every** user-reachable path, before the sink, without a
  fail-open branch: e.g. `self.check_access('read')` (v18+; older `check_access_rights` +
  `check_access_rule`) on the **non-sudo** record before `sudo()` is used; portal
  `_document_check_access(model, id, access_token)` before any read; a global multi-company rule.
- The sink is inert in context (value goes through `%s` params / `SQL("... %s", val)`, `t-out` of
  plain text) — say what makes it inert.
- The input is not user-controlled — traced to a trusted origin (XML data, `ir.config_parameter`
  written only by admin), not assumed.
- A test exists that performs the attack as `with_user(portal/internal)` and asserts
  `AccessError` — strongest form (a negative control).

When unsure, verify the v19 API with official docs (Context7 `/websites/odoo/19.0`) rather than memory.

## Severity rubric (Odoo mapping)

| Level | Prefix | Typical Odoo cases |
|---|---|---|
| Critical | `VULN` → BLOCK | `auth='public'`/`'none'` route returning other partners'/companies' data or allowing write; SQL injection from a public route; `safe_eval`/`eval` on request data; hardcoded production credentials |
| High | `VULN` → BLOCK | internal/portal user reads or writes other users'/companies' records via `sudo()` with a user-controlled domain or id; privilege crossing (portal → internal, user → manager); SQL injection reachable by an authenticated user; missing ACL row on a user-facing model |
| Medium | `REQUIRED` | stored XSS via `Markup`/`sanitize=False` in a back-office view; CSRF disabled on a state-changing form route; leak of low-value fields; high-impact case blocked by a confirmed constraint (manager group required, internal-only) |
| Low / Info | `WARNING` / `SUGGESTION` | uncommented but provably safe `sudo()`; verbose error to an internal user; missing `groups=` on a non-sensitive field; defense-in-depth with no reachable path |

**Usually NOT VULN** (needs unusual, demonstrated circumstances): anything requiring
`base.group_system` / `base.group_erp_manager` or shell access; self-XSS; open redirect alone;
enumeration that only confirms a record exists; "could matter if chained with several unproven
assumptions".

**Acceptance checklist before VULN** — all true, otherwise drop a level:
- [ ] attack path realistic and in scope (not dependent on prior compromise);
- [ ] attacker position obtainable (public visitor, portal user, ordinary internal user);
- [ ] impact demonstrated (which records/fields, whose), not asserted;
- [ ] counterevidence pass found no limiting control, or you explained why it does not hold;
- [ ] reachability shown in code (route `auth`, RPC-callable method, ACL that grants the model), not assumed;
- [ ] you would defend the rating to the client's tech lead.

**Downgrade, don't delete.** Constraint found → lower the level and say which constraint.
Missing evidence about exposure → lower **confidence**, keep the severity floor.
