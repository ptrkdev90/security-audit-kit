# Execution boundaries

Reading project files and writing new local audit artifacts are the initial workflow.
Scanner binaries process untrusted input; use patched versions and resource limits.
A Git repository is not a sandbox. npm lifecycle scripts, MSBuild targets, test fixtures,
Python imports, Maven/Gradle plugins and container builds can execute arbitrary code.
Inspect commands before running them. Use a disposable container/VM without host
credentials or privileged mounts for target code execution; Docker socket access is
privileged. Do not describe a subprocess timeout as a security sandbox.

Consult tool help for network use: vulnerability feeds and registries require network;
remote SAST, npm audit and hosted MCP may transfer code or dependency metadata.
Record approved destinations and shared-data categories; reuse explicit authorization.
Do not send secrets or source to a service merely because a tool is available.
Use resource-limited, authorized test accounts for runtime tests. Avoid data destruction,
credential guessing, broad crawling and production load tests. Log only sanitized data.
Do not attach raw secret-scan reports to public issues or commit audit outputs.
