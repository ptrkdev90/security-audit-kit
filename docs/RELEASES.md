# Release process and readiness

Use one independently reviewable commit per contract/feature and include relevant tests.
Keep manifests and README badges aligned at each release boundary. Maintain SemVer for
plugin releases; schema/report/template versions are tracked independently.

## Required checks

1. Repository/link/schema structure and helper regression tests.
2. Packaged CLI pipeline, negative cases, manual migration and hash reconciliation.
3. All-page visual review of representative English/German PDFs and long input.
4. Installation and update with a named Claude Code version in isolated configuration.
5. Real Claude audit behavior with representative projects and an actual user template.
6. Release notes, known limitations and migration instructions.

`claude_smoke.py` is opt-in and requires installed Claude Code. It creates a fresh temporary
CLAUDE_CONFIG_DIR and validates/installs/updates the local marketplace without model calls.
Exit 77 means unavailable, not passed. CI installs a pinned Claude Code version explicitly.
Local-path smoke tests do not verify GitHub transport, active-session reload, arbitrary
template fidelity or security-detection accuracy. Those remain separate release evidence.

Never claim a check passed because it is listed here. Keep `release-readiness.json` honest.
A release candidate can provide all implemented features while awaiting host/template
behavior checks. Only publish a stable 1.0.0 after those checks have actual evidence.
