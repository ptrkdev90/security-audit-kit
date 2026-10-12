# Scope and coverage

Record included repositories, branch/commit, dirty state, submodules, deployed services,
API versions, environments, test users/roles, available infrastructure and exclusions.
For monorepos enumerate all services, shared libraries and deployment roots.
Inventory exclusions are discovery choices, not automatic audit exclusions. Review
ignored configuration, vendored changes and generated security-sensitive code as needed.
Track Git LFS and submodules: absent contents mean blocked coverage, not reviewed code.

Use one coverage row per component/check, not an unsupported percentage of files read.
Fields: id, component, paths, check, applicability, status, method, evidence, limitations.
Statuses: pending, reviewed, blocked, not-applicable. Reviewed means that stated check
was completed with cited evidence; it never means the component is secure.
Not-applicable requires a reason. Blocked requires a reason and next evidence needed.
Record tool-specific skips and parsing errors separately from manual-review coverage.
Finish when all rows are reviewed, blocked or justified not-applicable and all
candidates are triaged. State the actual audit boundary in the report title.
