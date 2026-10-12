# Architecture views

Use `architecture.json` as the diagram source. Describe stakeholders, security concerns,
components, trust boundaries and flows. Follow [Architecture schema](../assets/schemas/architecture.schema.json).
Record authentication, authorization, sensitive data, protocol and failure behavior for
each flow. Do not infer a deployed control from a design document or UI implementation.

Mark every component, boundary and flow `observed`, `inferred` or `unknown`. Observed
assertions need registered evidence; inferred/unknown assertions need explicit limitations.
An observed source flow may still have unverified deployment properties; say so in limits.
Use source/configuration references and dated runtime evidence separately.

Keep identifiers stable, ASCII letters/numbers/underscore/hyphen, beginning with a letter.
Use separate small views for large systems. Record external identity, browser, server,
storage, background workers and third-party processing where applicable. State omitted
subsystems. A diagram is a model, not proof that the environment matches it.

Link high-risk flows to threats and coverage. Include role escalation, tenant transitions,
error/fallback paths and asynchronous operations. Use the generated Mermaid view for
GitHub/Markdown; use the local SVG renderer for offline HTML/PDF. Never load CDN scripts
or send architecture to an external diagram service without authorization.

Generate architecture and threat flowcharts in a fresh directory:

```sh
python3 <skill-directory>/scripts/diagrams.py <audit>/architecture.json --plan <audit>/audit-plan.json --output-dir <audit>/diagrams
```

Each threat's `flow_ids` selects actual modeled edges. With no flow evidence, keep an
explicit source-only hypothesis in the threat table; do not invent an attack sequence.
The SVG view is intentionally limited to 20 components/flows; split larger systems into
separate documented views. Diagram labels may be shortened; report tables retain full text.
