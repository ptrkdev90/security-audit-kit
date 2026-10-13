# Required start dialog

For a bare command invocation, stop before audit execution and collect three explicit
choices. Do not inspect the target, initialize files or run capability probes first.
Read only the skill/intake instructions needed to ask. Use Claude Code's available
question interface (for example AskUserQuestion), or ask the same questions in plain
text when no question tool is available. Do not invent a host-specific tool.

Ask in the conversation language, grouping the three questions into one short dialog:

1. **SOC-2-Readiness:** include it, or perform the technical security audit only?
2. **Export:** Markdown/JSON only, additionally HTML, additionally PDF, or both HTML and PDF?
3. **Design:** standard neutral layout, installed template skill, or supplied template file?

German example:

> Bevor ich das Audit starte, brauche ich drei Entscheidungen:
> 1. SOC-2-Readiness einbeziehen: Ja oder Nein?
> 2. Ausgabe: Markdown/JSON, zusätzlich HTML, zusätzlich PDF oder HTML + PDF?
> 3. Design: Standardlayout, installierter Template-Skill oder eigene Vorlagendatei?
>    Bei eigener Vorlage bitte den Skill-Namen oder Dateipfad angeben.

All three questions are mandatory even when no additional export is chosen: standard
layout is a valid design choice for Markdown. Markdown and structured evidence remain
canonical artifacts; an additional export does not replace them. Explain that SOC 2
means readiness evidence, never an attestation, when the choice needs clarification.

## Wait and resolve

- Wait for an explicit choice for every question. No reply, timeout, dismissed question
  tool or absent answers is not a decision. End the turn with the questions pending;
  do not start independent audit work while waiting.
- Accept explicit user delegation (for example "use the standard layout"); do not
  treat silent omissions as delegation. Ask only the unanswered questions after a
  partial reply. Do not repeatedly ask answered questions within the same intake.
- If a template skill/file is selected, obtain its exact name/path before starting.
  Do not silently replace a requested design with the default. Once a specific template
  is named, inaccessible resources or renderers become explicit export blockers under
  the report-export workflow; the agreed technical audit can proceed.
- A cancellation means no audit execution and no audit outputs.
- Treat a later bare invocation as a new intake, including when an earlier audit used
  SOC 2 or a template. Only an explicit resume of the same audit reuses recorded choices.
- With a non-bare invocation, honor the current task's choices and existing execution
  rules. Never ask again for an export/design/SOC 2 choice already explicitly supplied.

## Apply and record

After all choices are resolved, initialize the audit and record SOC 2 enabled/disabled,
additional formats, layout mode, and exact custom template name/path in scope.md and
checkpoint.md. Record that these were explicit intake answers. Follow the normal audit
workflow, selected compliance module and requested export workflow.

The choices authorize the requested audit outputs, not target builds, production attacks,
software installation, external uploads or signing. Author/reviewer identities remain
unknown unless supplied; sign-off remains unsigned. Never change the selected export
because a renderer is missing: retain the choice, report the blocker and preserve the
canonical artifacts. No promise of arbitrary-template fidelity or successful export is
made solely by completing the dialog.
