# .NET review

Inspect solution/project files, SDK/runtime target, framework support and package locks.
Review authentication schemes, JWT validation, fallback policies, AllowAnonymous,
authorization handlers, resource-based authorization and middleware ordering.
Trace EF/raw SQL and interpolated queries; inspect ProcessStartInfo, file paths,
XML readers, serializers/type handling, Razor/HTML helpers and regex/timeouts.
Check model binding/overposting, antiforgery where cookies authenticate writes,
Data Protection key persistence, forwarded headers/proxies and exception pages.
Review IConfiguration precedence, environment overrides and fail-open credential or
endpoint fallback. User Secrets are a development mechanism, not production secret storage.
Never read the user's secret store during the audit. Check logging for token/PII exposure.
Review MSBuild targets before restore/build/test; these may execute code.
Use the installed SDK's `dotnet list package --help` or `dotnet package list --help`.
Select vulnerable/transitive options supported by that SDK; record restore/network effects.
