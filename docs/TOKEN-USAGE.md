# Context and token efficiency

Load only the current phase and applicable stack references. Keep raw scanner output in
local artifacts; read focused slices with full surrounding security context. Normalize and
deduplicate scanner alerts for triage while preserving counts, package paths and originals.
Use helpers for deterministic inventory, references, diagrams, hashing and rendering.

Never cut coverage to meet a token budget. Do not replace full data-flow review with grep,
drop high-impact suspicions, or trust summaries/cache without inspecting their provenance.
The lean entry skill changes instruction-loading size; it does not demonstrate model token
savings. Real measurements need identical repositories, model/version, tool setup, prompts
and outcomes, including false positives and missed high-risk controls.

Run `python3 scripts/benchmark_context.py` for entry-text proxies. For real comparisons
pass `--samples observations.json`. Each pair needs the same `case`, `model`,
`prompt_sha256`, `environment_sha256`, `trial`; use `variant` baseline/candidate,
`input_tokens`, `output_tokens`, `missed_high_impact`, `false_positives`,
`expected_checks`, `reviewed_checks`. Record plugin/model/tool versions in the environment
fingerprint and preserve raw usage receipts locally. Include tool content in provider
input tokens; do not double count it. Distinguish cache billing in the raw receipts.
Do not fabricate token observations or expected outcomes. The comparison flags reduced
coverage or increased false positives/missed high-impact findings even if tokens drop.
