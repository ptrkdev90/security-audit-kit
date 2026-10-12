# Optional compliance evidence review

Use this module when the user requests SOC 2 readiness, ISO 27001 alignment or another
named framework. Continue the technical audit independently. Establish framework,
version, service/system boundary, selected categories and period. Never silently turn
a source audit into a formal assurance engagement.

SOC 2 examines controls relevant to Security, Availability, Processing Integrity,
Confidentiality and Privacy. Scope categories with the owner and examiner. Source
review can support evidence for access controls, secure change, monitoring, vulnerability
management and data protection, but source evidence alone does not establish operating
effectiveness. Policies, ownership, access reviews, incident records, restore exercises,
change approvals and retained operational evidence need separate evaluation.

Use assets/templates/compliance-matrix.csv. Each row must contain framework version,
criterion (only if verified against authoritative criteria), local control, evidence
source, evidence date/period, owner, assessment, limitations and next evidence needed.
Use supported, partial, missing-evidence, not-applicable or not-assessed. Supported means
only that the recorded local evidence supports this specific assertion; it is not a
formal compliance opinion. Do not count missing evidence as a proven control failure.
Do not invent control IDs, copy proprietary standards or calculate a compliance score.

Suggested evidence topics: account lifecycle and least privilege; PR approval and
release provenance; vulnerability triage/remediation; monitoring and incident response;
backup/restore and resilience; data inventory, retention and deletion; supplier controls.
Technical observations may map to more than one framework, but mappings are tentative
until checked against the selected version. Keep an organizational evidence backlog.

A formal SOC 2 report is issued through a qualified CPA examination, not by this skill.
Other frameworks have different certification/legal processes. Report this work as a
technical review and optional readiness/evidence assessment, never as certified compliance.
