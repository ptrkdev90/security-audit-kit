# Changelog

## 0.5.0

- Lean phase routing and conservative, allowlisted snapshot/resume helper.
- Explicit context/tool/scope invalidation and snapshot expiry.
- Text-size proxies and paired real-usage benchmark support with quality guardrails.
- Actual model token savings remain unmeasured.


## 0.4.0

- Structured architecture with evidence, trust boundaries and explicit uncertainty.
- Local Mermaid/SVG views, safe labels, and threat-to-flow references.
- Schema/reference tests; no claims of deployed-state verification from diagrams.


## 0.3.0

- Findings 1.2: structured evidence and threat references, typed confirmation checks.
- Threat-driven audit plan and required-domain reconciliation.
- Regression tests for fabricated references, scanner-only confirmation and missing scope.
- Existing 1.1 reports remain readable; new audits use 1.2. Migrate manually before exporting.


## 0.2.0

- Separate security vulnerabilities, dependency advisories, control gaps, hardening and evidence gaps.
- Record verification basis, exploitability, severity rationale, verification limits and bounded refutation scope.
- Reject scanner-only confirmation of application vulnerabilities and unsupported demonstrated exploitability.
- Preserve dependency alert counts separately from unique advisories and affected packages.
- Require durable final output and source/report reconciliation; retain optional template-based PDF export.
- Clarify CI/SOC 2 inference, prohibited secret reads, stale build output and scoped negative searches.
- Add seven regression tests (16 total) and live-agent evaluation scenarios.

### Findings format migration

Findings 1.1 adds six fields: kind, verification_basis, exploitability,
severity_rationale, verification_limits and refutation_scope. Empty refutation_scope
is allowed except for refuted records. Empty locations are allowed for non-code
observations. Coverage and tool-runs remain at 1.0.

Legacy findings 1.0 can be validated provisionally but cannot pass --final.
Manually classify and reassess each record, retain IDs/evidence, then change findings
schema_version to 1.1. Do not merely upgrade the version string. See the classification
reference for confirmation criteria. This is a breaking finalization change for old audits.

### Verification limits

Repository structure and 16 helper tests passed locally. Live Claude behavior for these
new instructions and exports using actual user templates has not been re-evaluated.
The validator checks consistency of records, not truth of security or compliance claims.
