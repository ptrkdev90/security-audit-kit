# Documentation style

Write for two audiences: concise decisions for owners; reproducible detail for engineers.
Use active verbs, short sentences, consistent terms and numbered remediation steps.
Define acronyms on first use. Preserve severity, confidence, prerequisites and uncertainty.
Keep headings, captions, evidence citations and tables consistent across formats.

Use plain English or plain German as requested. ASD-STE100 can guide English wording when
requested; do not claim vocabulary/rule conformance without a complete applicable check.
Do not apply its English vocabulary rules mechanically to German reports. A style guide
cannot establish formal compliance with technical-documentation standards.

Include document ID/version/status, snapshot, timestamps/timezone, audience, author when
provided, evidence references, limitations, change history and unsigned review fields.
Use accessible text alongside every diagram. Keep sensitive content out of examples.

## Required editorial checks

- Outcome: state the decision, verified impact and major blockers first.
- Finding: prerequisites, reachable path, examined defenses, evidence and limits.
- Action: concrete owner role, proposed change and observable retest result; do not invent deadlines.
- Terminology: keep severity/status labels consistent and define RLS, RBAC, SAST and other acronyms.
- Diagrams: caption the viewpoint, snapshot and uncertainty; supply full textual equivalents.
- Accessibility: semantic headings, readable contrast, descriptive captions and no color-only severity.
- Localization: translate narrative/headings without changing IDs or canonical status names.
- Document control: preserve version history, review state and the exact exported snapshot.

Use optional `audience` and `glossary` fields in report-source.json. Keep the narrative
and machine artifacts consistent. Default PDF is not tagged PDF/UA; no PDF/UA or PDF/A
conformance is asserted. Custom accessibility/archival requirements need a capable renderer
and a separate format-specific validation step.

When a standard profile is requested, create documentation-profile.json from its template,
select editions from authoritative sources, distinguish full-text review from public
abstracts, and cite evidence. Do not declare formal conformity from this helper's checks.
