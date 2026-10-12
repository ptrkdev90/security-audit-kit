# Finding verification

1. Identify exact file/line and snapshot. Trace entry point to sensitive sink.
2. Establish attacker identity, controllable input and environmental prerequisites.
3. Inspect all relevant validation/encoding/authorization and downstream behavior.
4. Attempt to refute the candidate with real counterevidence, not assumed defenses.
5. Produce a safe minimal reproduction or an explicit source-level reasoning chain.
6. Assign severity based on impact and prerequisites, separately from confidence.
7. Search variants and link duplicates to one root cause when appropriate.

Confirmed requires a defensible attack path and observed impact or complete source
reasoning. Reproduction is preferred, not fabricated when runtime is unavailable.
Record whether validation is runtime or source-based and its limits. Suspected needs
next steps; refuted needs specific counterevidence. Accepted-risk requires an explicit
owner decision and keeps the risk visible. Fixed needs post-change verification.
Avoid invented CVSS scores/CVEs. If CVSS is used, specify version and full vector.
Use CWE only when the classification fits; it is optional. Keep hardening observations
separate when no security impact can be established. Redact secrets and personal data.
