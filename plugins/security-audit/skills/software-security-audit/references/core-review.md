# Core security review

For each applicable check trace inputs to sensitive operations and verify defenses.

- Authentication: token issuer/audience/signature/expiry, recovery, sessions, revocation.
- Authorization: per-object checks, server-side roles, tenant scoping, batch/export paths.
- Injection: queries, OS processes, templates, expressions, path operations and parsers.
- Data: secret handling, logging, error responses, retention, encryption, backups.
- Files: traversal, symlink escapes, archive extraction, MIME ambiguity, storage permissions.
- Outbound requests: SSRF, redirect handling, destination validation, cloud metadata access.
- Cryptography: standard primitives, secure randomness, key storage, nonce reuse.
- Deserialization: untrusted types, polymorphic binding, unsafe loaders and executable formats.
- Business logic: state transitions, replay/idempotency, ordering, concurrency, money/units.
- Availability: bounded work, decompression, regex, pagination, queues, request size/timeouts.
- Configuration: fail-closed checks, debug endpoints, wildcard grants, insecure fallback.

Do not filter out DoS, rate limiting or open redirects wholesale. Evaluate real impact
and prerequisites. Record lower-priority hardening separately from vulnerabilities.
