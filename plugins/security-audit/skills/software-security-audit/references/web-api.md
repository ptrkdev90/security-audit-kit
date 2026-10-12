# Web and API review

Build a route inventory from routers/controllers/OpenAPI and verify it against source.
Inspect anonymous, role-protected, administrative and tenant-specific routes, including
GraphQL resolvers, websocket messages and background dispatch endpoints.
Check object and property authorization, mass assignment, filtering/export scope,
CSRF for cookie-based state changes, cookie attributes, CORS and cache behavior.
For XSS trace untrusted text into HTML/DOM/template contexts and validate contextual
encoding. Check CSP as defense-in-depth, never as proof that unsafe rendering is safe.
Verify OAuth redirect constraints, state/PKCE as applicable, webhook authentication and
replay handling, token storage and sensitive data in browser caches/offline storage.
Test alternate methods, content types, error paths and bulk endpoints in an authorized
fixture. Establish runtime scope before active requests. Document absent runtime access.
