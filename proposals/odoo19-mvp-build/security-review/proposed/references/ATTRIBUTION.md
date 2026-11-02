# Attribution

Parts of this skill (closure states, "what does not rule out a candidate", severity calibration,
fix verification gates, diff-scoped review rules) are adapted from the Strix project:

- Source: https://github.com/usestrix/strix — files
  `strix/skills/analysis/counterevidence.md`, `strix/skills/analysis/severity_calibration.md`,
  `strix/skills/analysis/fix_verification.md`, `strix/skills/scan_modes/diff.md`
- Commit: `6b7ae2e`
- License: Apache License 2.0 — https://www.apache.org/licenses/LICENSE-2.0
- Copyright: the Strix authors (usestrix). The upstream repository ships no NOTICE file.

Changes: text condensed and rewritten; Jinja templating and Strix tool calls
(`record_coverage`, `agent_finish`, CVSS fields, `fix_before`/`fix_after`) removed; examples
replaced with Odoo 19 equivalents (ACL, `ir.rule`, `sudo()`, controllers, `cr.execute`/`SQL`,
`Markup`); severity mapped to the skill's `VULN`/`REQUIRED`/`WARNING`/`SUGGESTION` prefixes.
