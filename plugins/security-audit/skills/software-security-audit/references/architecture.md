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
