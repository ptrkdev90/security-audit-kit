# Audit format migration

Plugin SemVer, per-artifact schema versions, report version and template version are
independent. Updating a plugin does not upgrade old findings or invalidate old reports.
New renderers require the current evidence contract; legacy reports remain historical.

| Artifact | Current schema | Migration |
|---|---|---|
| findings | 1.2 | Manually reassess classification and register evidence/threat IDs |
| coverage / tool-runs | 1.0 | Preserve supported records |
| evidence / audit-plan / architecture | 1.0 | Populate from actual evidence; do not invent |
| report-source / report-metadata | 1.0 | Complete narrative, timestamps, snapshot and unsigned state |
| report-model / export receipts | 1.0 | Regenerate from canonical sources |

Create a review JSON with `reviewed_by`, `reason` and complete replacement objects under
`findings`, `evidence`, `audit-plan`, `architecture`, `report-source`, `report-metadata`.
Preserve finding IDs and report ID; increment report_version and add document_history
with date, author if supplied, and change reason. Unknown reviewer/approver identities
remain null. Migration does not transfer approval or signatures to a changed document.

```sh
python3 <skill-directory>/scripts/migrate_audit.py <old-audit> --review-file <review.json> --output <new-audit>
```

The helper retains originals under previous-version, copies supporting scope/coverage,
records source hashes and validates the migrated draft. It never chooses classifications
or drops findings. Failed validation retains a new draft for correction; original files
are unchanged. Re-export, reconcile and inspect layout after a successful migration.

Receipts record exporter plugin version, input schema versions, template identity and
source/output hashes separately from the audit plugin version in report metadata. Hashes
prove artifact identity, not independent authenticity; preserve trusted originals/receipts
and use authorized signing when authenticity is required.
