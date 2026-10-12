# Classify what the evidence actually establishes

Use findings schema 1.1. Record kind independently from status, severity and confidence.

| kind | Confirmed means | Does not establish |
|---|---|---|
| security-vulnerability | Defensible attacker-controlled path and security impact, verified by full source trace or safe runtime test | Complete security of other paths |
| dependency-advisory | Installed version matches an advisory, with lockfile/version and scanner evidence | Reachability or exploitability in this application |
| control-gap | A specified expected control is absent/ineffective in the inspected scope, with evidence | Its absence in uninspected services or a formal compliance failure |
| hardening | A specific improvement is supported by context | A demonstrated attack |
| evidence-gap | A required question remains unresolved due to missing evidence | That the underlying control failed |

For non-attack observations, explicitly put "Not applicable: <reason>" in attack_path
and prerequisites rather than inventing an attacker narrative. Locations may be empty
for organizational evidence gaps; cite the requested evidence and inspected scope.
Confirmed vulnerability requires precise locations, examined defenses and established
exploitability. A complete source trace may suffice without runtime; record the runtime
limitation. Scanner output alone never confirms an application vulnerability.

## Dependency triage

Record advisory identifier/source when supplied, package/version, direct or transitive
path, production/dev classification, affected feature, existing defenses and reachability.
Separate scanner raw counts, unique advisories, affected packages and deduplicated root
causes. Do not call every dependency node a separate vulnerability. Dev dependencies
can still expose build/CI/dev servers; investigate that path rather than dismiss them.
Use exploitability unassessed until evaluated. Report scanner-rated severity as such;
explain application severity in severity_rationale without invented CVSS or upgrades.
If the vulnerable functionality is not reachable in the examined runtime, retain the
confirmed dependency advisory with that bounded limitation; do not refute its existence.

## Common inference errors

- No tests/lint/typecheck/dependency job in inspected CI is a control-gap, not by itself
  a medium security vulnerability. Check other workflows or external evidence and state
  the inspected scope. Rank SOC 2 gaps only with a stated assessment basis, not "largest".
- File names .env.*, a hardcoded email allowlist or localhost redirect URI alone are
  not secret leaks or confirmed flaws. Examine authorized content, privilege enforcement,
  deployed settings and context. Respect prohibited file reads; document the resulting gap.
- Absence of innerHTML/eval proves only absence of those patterns in the searched files.
  Refuting a concrete DOM-XSS candidate needs its actual source-to-sink path and defenses.
- Unbuilt dist/ artifacts support claims only about that artifact. Record provenance;
  do not treat stale output as proof about HEAD or deployment.
- UI-only authorization is a suspected backend issue until server/model controls are
  traced or safely tested. ReadExplore documentation is not proof that RLS is bypassed.

## Status and reporting

Separate confirmed vulnerabilities, confirmed advisories, control gaps/hardening,
unresolved candidates and missing evidence in report.md and the final response.
Use conditional impact for suspected cases. Verification_limits states the boundary
of every conclusion, even when confirmation rests on source. Refuted items require
refutation_scope; general absence searches belong in coverage, not invented refutations.
Accepted-risk requires an explicit owner decision; fixed requires post-change evidence.
Do not infer either from a proposed recommendation.

## Existing records

Schema 1.0 remains readable for interim review. Finalization requires 1.1. Preserve IDs
and evidence, manually add kind, verification_basis, exploitability, severity_rationale,
verification_limits and refutation_scope to each item, and reassess status. Set only the
findings schema_version to 1.1; coverage and tool-runs remain 1.0. Never auto-convert
confirmed scanner hits into confirmed vulnerabilities. The validator checks recorded
consistency, not the truth of supplied evidence.
