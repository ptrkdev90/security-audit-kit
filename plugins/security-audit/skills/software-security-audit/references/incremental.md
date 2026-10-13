# Persistence and snapshots

Record commit, working tree, scope boundaries, excluded/forbidden paths, tool versions,
rule/feed versions, deployment identity and the evidence period. Store checkpoints in the
audit directory, outside the target source. Record completed coverage IDs, remaining work,
blockers and the next safe command; do not retain secret values or full source dumps.

Read project restrictions before hashing files: hashing reads content. Use an explicit
allowlist of permitted regular files, no symlinks or credential files. Include relevant
configuration, authorization middleware, lockfiles and CI/IaC along with reviewed code.
Record exclusions and missing context. A dirty tree can be audited; record its identity.

Resume checks are conservative. Changed content, scope, instructions, tool/rule versions,
external deployment or expired feed evidence invalidates previous assumptions. Re-review
changed paths plus callers, callees, shared defenses, generated provenance and deployment
boundaries. Unchanged source does not prove unchanged runtime. Record externally unverifiable
state as blocked. A checkpoint is planning evidence, never automatic security approval.

Use `checkpoint.py` only after approving permitted content reads. Supply a JSON array
of relative allowlisted paths and a context JSON object describing scope, constraints,
plugin version, tool/rule/feed versions and deployment/evidence period. Only a context
hash is retained; store a sanitized description in scope.md for interpretability.

```sh
python3 <skill-directory>/scripts/checkpoint.py --root <project> --allowlist <allowlist.json> --context <context.json> --output <audit>/snapshot-start.json
python3 <skill-directory>/scripts/checkpoint.py --root <project> --allowlist <allowlist.json> --context <context.json> --previous <audit>/snapshot-start.json --output <audit>/snapshot-resume.json
```

Git state, root, allowlisted hashes, context, helper identity or age changes invalidate
reuse. A default 24-hour freshness ceiling is a planning control, not evidence that
vulnerability feeds are current. `eligible-for-manual-review` requires human/agent
reconciliation, including new unlisted files and external state. Store completed and
pending coverage IDs, blockers, decision rationale and next action in checkpoint.md.
