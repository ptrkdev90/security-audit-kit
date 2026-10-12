# Scanner playbook

## Before running

Discover installed tools; inspect their versions/help. Do not auto-install or auto-fix.
Select actual target roots. Keep output outside the target and inspect ignore/suppression
files. Record tool version, command, UTC timestamp, exit code, rules/database version,
network use, skipped files, parsing errors and sanitized output in tool-runs.json.
An empty result from a failed scan is not clean. Interpret exit codes using that version's
documentation. Read tool output files before truncating summaries.

## Examples, not an automatic runner

Replace path placeholders with correctly quoted absolute paths. These are individual
commands. Run only within the authorized execution/network scope.

```sh
semgrep scan --config /path/to/reviewed-local-rules --metrics=off --disable-version-check --json --output /path/to/audit/semgrep.json /path/to/project

gitleaks dir /path/to/project --redact --report-format json --report-path /path/to/audit/gitleaks-tree.json

gitleaks git /path/to/project --redact --report-format json --report-path /path/to/audit/gitleaks-history.json

trivy fs --scanners vuln,misconfig --format json --output /path/to/audit/trivy.json /path/to/project
```

Semgrep: use local trusted rules for a local-only workflow. Registry rules need network;
`--metrics=off` is not a general network blocker. Record rule-set identity/digest,
unsupported languages and ignored files. This kit bundles no universal ruleset.
Gitleaks: scan working tree AND available Git history. Redaction is required. Inspect
allowlists/baselines and shallow-clone boundaries. Verify redaction before sharing files.
Trivy: DB downloads may need network; a cached offline DB can be stale. Disable the
secret scanner here to avoid accidental secret-value artifacts; use redacted Gitleaks.
CodeQL: useful where supported, including C#. Database creation may build target code;
review execution scope and licensing before running. Record query pack and extraction gaps.
.NET: choose SDK-supported vulnerable/transitive package listing; do not silently restore.
npm: `npm audit --json` sends dependency metadata to the configured registry. Do not run
`npm audit fix`. Python: use a suitable dependency scanner for the pinned environment;
avoid resolving/installing unknown packages just to produce a report.

No scanner is mandatory across all stacks. If an essential security domain lacks a
working tool, perform manual checks where possible and mark the residual gap.
