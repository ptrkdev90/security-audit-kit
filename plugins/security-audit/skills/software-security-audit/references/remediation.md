# Remediation and re-audit

When remediation is requested, preserve local edits and keep each fix focused on its
root cause. Identify compatibility and behavior changes. Add a meaningful regression
test when feasible; avoid implementation-mirroring tests. Run only authorized code in
an appropriate environment. Re-review variants, exception paths and deployment needs.
Record before/after snapshots, test commands/results and residual risk. Mark a finding
fixed only after validation; a proposed patch is not a verified fix. For exposed secrets,
code removal alone is insufficient: rotation/revocation and history handling require
owner action. Do not perform external rotations or deployments without authorization.
