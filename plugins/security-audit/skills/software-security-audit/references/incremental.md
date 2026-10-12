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
