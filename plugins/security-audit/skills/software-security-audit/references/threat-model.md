# Threat modeling

Map trust boundaries rather than directories. Enumerate anonymous users, authenticated
users, privileged operators, other tenants, compromised integration partners and CI actors.
Record asset, entry point, attacker control, intended authorization, transition across a
trust boundary and expected security property. Prioritize high-value flows:
login/token refresh, password recovery, administrative changes, exports, orders/payments,
file import/upload, webhooks, background jobs, secrets and cloud deployment.
Trace identity propagation and server-side checks at every privileged operation.
Account for retries, concurrent requests, partial failures, caches and stale permissions.
Link abuse cases to coverage rows. Distinguish source evidence from assumptions about
network topology, identity providers, TLS termination or managed-service configuration.
