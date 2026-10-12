# Threat-driven coverage

Create `audit-plan.json` before substantive review. Record assets, actors, reachable
entry points, abuse cases, priority and linked coverage IDs. A threat is a hypothesis,
not a finding. Include external components even when evidence is blocked.

Select required domains from the observed stack: identity/session, object/tenant
access, input/output, data/secrets, business logic, dependencies, configuration,
CI/CD, runtime/deployment. Use the exact check names in `required_domains` and
`coverage.json` so omitted domains are detected. Add component-level rows for each
applicable domain. Justify `not-applicable`; retain blocked infrastructure checks.

For each high-risk flow inspect success, denial and failure paths, upstream defenses
and privilege changes. Link findings to the threats they establish or refute. Review
variants of verified root causes. Perform a second reconciliation of inventory,
entry points, threat map and coverage before finalization; a schema cannot detect
an entry point nobody inventoried. No universal checklist proves exhaustive coverage.

Read optional framework source/version before assigning requirement IDs (for example
OWASP ASVS). Never claim an ASVS level from partial review or infer SOC 2 effectiveness
from source code. Keep operational evidence requirements in the compliance matrix.
