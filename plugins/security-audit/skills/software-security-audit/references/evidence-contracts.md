# Evidence contracts

Register sanitized evidence in `evidence.json` with stable IDs, type, locator, snapshot,
observation time, summary and limitations. Hash preserved sanitized artifacts when useful;
a hash proves identity, not correctness. Never store secret values as evidence.

Use `evidence_ids` and `threat_ids` in findings schema 1.2. Preserve readable evidence
citations too. Confirmed source-trace vulnerabilities require registered source evidence;
runtime-test confirmation requires runtime evidence. Scanner evidence alone supports an
advisory, not application exploitability. Record affected installed version, advisory ID,
production/development path and reachability separately in the finding's verification.

Keep severity rationale specific to this record kind and environment. Confidence measures
confidence in the assertion, not impact. Missing evidence proves only an evidence gap.
Accepted risk needs a supplied owner decision, scope, date and review trigger. Fixed needs
a new snapshot, retest and variant checks. Refutation is bounded to the examined path.

Legacy findings need manual classification before upgrading; never infer exploitability
or invent evidence from scanner output. See the release migration guide.
