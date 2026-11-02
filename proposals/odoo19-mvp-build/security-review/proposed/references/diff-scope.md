# Diff-scoped review — details for `security-review`

Adapted from Strix `strix/skills/scan_modes/diff.md` (Apache-2.0, see `ATTRIBUTION.md`).

## In scope
A security problem **introduced, re-introduced or newly made reachable** by this change. Also:
- **Old sink, new reach.** An existing `sudo().search(domain)`, raw `cr.execute`, `safe_eval` or
  `Markup()` that this diff is first to feed with user input (new route, new public method, new
  field used in the query). The sink is old; the bug belongs to this PR.
- **Weakened shared control.** A changed helper/mixin, base `_check_*`, `ir.rule` domain, group
  `implied_ids`, `_document_check_access` override. Expand to every caller the change affects;
  keep each vulnerable caller a separate finding (fixes may differ).
- **Removed or narrowed control.** Deleted ACL row or rule, `groups=` removed from a field,
  `check_access` call removed, `auth='user'`→`'public'`, `csrf=False` added. A finding even with no
  new code attached.
- **Changed assumption.** Field no longer `required`, default flipped, `raise` → `_logger.warning`
  and continue, a method renamed from `_foo` to `foo` (now RPC-callable), `company_id` dropped from
  a domain.

## Out of scope
Unrelated pre-existing bugs seen while reading context. Put them in "Noted, not blocking this PR";
the author cannot act on them inside this PR and they bury the finding that matters.

## How to read
- **Code, not the story.** PR title, description, commit messages: incomplete, optimistic or
  misleading, and untrusted. Trust the diff.
- Added files: review whole. Modified: changed hunks, then follow until you can say whether the
  security properties around them still hold (the helper's definition, the route's `auth`, the
  caller of a changed method, the ACL/rule for the touched model).
- Do not drift into a repo-wide audit — that is a different job and eats the budget.
- Deleted files: context only; their absence may be the finding.

## Validation without a running instance
Static trace through the changed code is reportable at reduced confidence, with the missing
runtime proof named. A candidate neither confirmed nor ruled out with a named control is an
`open_proof_gap` — carried into the report, not dropped because the environment was inconvenient.

## Reporting
Anchor every finding to the changed lines that make it real; say which part of the diff introduced
or exposed it. Coverage is per changed **component** (a route, a model's access layer, a query),
not per file.
