# Azure, containers and infrastructure

Inspect available Bicep/Terraform/ARM/Kubernetes/container configuration. Map identities,
RBAC assignments, managed identities, Key Vault access, storage permissions, public
endpoints, network restrictions, encryption, diagnostics and secret references.
Review wildcard permissions, privileged containers, host mounts, service accounts,
image provenance, unpinned tags and exposure of database/admin services.
For Fabric and integration pipelines inspect credentials, service principals, storage
access, data classification and logs. For Salesforce integrations inspect OAuth scopes,
credential handling, record authorization assumptions and outbound destination control.
Do not infer effective deployed permissions from templates alone. Cloud inspection
requires scoped account access already authorized for this audit; never enumerate
unrelated subscriptions or tenants. Missing deployment access is a recorded gap.
