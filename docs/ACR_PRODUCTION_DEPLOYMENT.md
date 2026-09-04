# ACR and Production Deployment Guide

This guide describes how to promote tested AI Value Hub source into versioned OCI images in Azure Container Registry (ACR), and which controls must be completed before a client production launch.

## Scope

The repository currently provides:

- Dockerfiles for the API and frontend.
- ACR cloud builds with immutable Git SHA or release tags.
- A Bicep foundation for ACR, Container Apps Environment, Storage, Key Vault, monitoring, and optional PostgreSQL.
- A script to update existing Azure Container Apps to a specific image tag.

The Bicep foundation does not create the API and frontend Container Apps. Create those applications through the client's approved platform pipeline, then use the image update script in this repository.

## Prerequisites

- Azure CLI authenticated to the client tenant and subscription.
- Contributor on the deployment resource group to provision the foundation.
- `AcrPush` or equivalent build permission on ACR for image publication.
- Permission to assign `AcrPull` to the Container Apps managed identity.
- Client-approved names, Azure region, DNS names, TLS certificates, and frontend/API URLs.
- A tested release commit. Do not publish images from a dirty working tree.

Select the subscription explicitly:

```powershell
az login --tenant <tenant-id>
az account set --subscription <subscription-id>
az account show --output table
```

## 1. Deploy the Azure foundation

Review `infra/main.parameters.json`; use client-specific names and tags. Then run:

```powershell
.\infra\deploy-foundation.ps1 `
  -ResourceGroupName "rg-ai-value-hub-test" `
  -Location "eastus"
```

Capture the deployment outputs, especially the ACR login server, managed identity resource ID, Key Vault name, Storage account name, and Application Insights connection string.

The default template is suitable for a test foundation. Network isolation, production database configuration, and workload resources still require client-specific design.

## 2. Publish versioned OCI images

The script uses ACR Tasks, so Docker is not required on the operator workstation. The frontend API URL is embedded during the Vite build and must be reachable from users' browsers.

```powershell
.\infra\push-to-acr.ps1 `
  -ResourceGroupName "rg-ai-value-hub-test" `
  -AcrName "<acr-name>" `
  -ApiBaseUrl "https://api.test.contoso.com" `
  -ImageTag "1.0.0"
```

If `ImageTag` is omitted, the script uses the first 12 characters of the current Git commit. It rejects `latest` to keep deployments and rollbacks traceable.

Published names follow this convention:

```text
<acr>.azurecr.io/ai-value-hub/api:<tag>
<acr>.azurecr.io/ai-value-hub/frontend:<tag>
```

For a production pipeline, also generate an SBOM, scan both images, sign their digests, and promote the exact approved digests rather than rebuilding the release.

## 3. Grant Container Apps access to ACR

Use managed identity instead of ACR administrator credentials:

```powershell
$acrId = az acr show --name "<acr-name>" --query id --output tsv
$principalId = az identity show `
  --resource-group "rg-ai-value-hub-test" `
  --name "<managed-identity-name>" `
  --query principalId --output tsv

az role assignment create `
  --assignee-object-id $principalId `
  --assignee-principal-type ServicePrincipal `
  --role AcrPull `
  --scope $acrId
```

Configure each Container App registry entry to use that managed identity. Do not enable the ACR admin account or store registry passwords in application settings.

## 4. Configure the workloads

Configure at least these API settings:

```text
AIHUB_AUTH_PROVIDER=demo                         # test only
AIHUB_ALLOWED_ORIGINS=https://app.test.contoso.com
AIHUB_DB_PATH=/data/aihub.db                    # test only
AIHUB_STORAGE_ACCOUNT_NAME=<storage-account>
AIHUB_STORAGE_CONTAINER=documents
APPLICATIONINSIGHTS_CONNECTION_STRING=<Key Vault reference or platform setting>
```

Use secret references backed by Key Vault for every secret. Prefer managed identity for Storage, Key Vault, ACR, PostgreSQL, and future Microsoft Foundry access.

Add HTTP liveness and readiness probes for the API at `/health` on port `8000`. Configure the frontend probe on `/` at port `80`. Use HTTPS-only ingress, custom domains, and client-approved certificates.

## 5. Deploy an approved version

```powershell
$loginServer = az acr show --name "<acr-name>" --query loginServer --output tsv

.\infra\update-container-apps.ps1 `
  -ResourceGroupName "rg-ai-value-hub-test" `
  -ApiContainerAppName "ai-value-hub-test-api" `
  -ApiImage "$loginServer/ai-value-hub/api:1.0.0" `
  -FrontendContainerAppName "ai-value-hub-test-frontend" `
  -FrontendImage "$loginServer/ai-value-hub/frontend:1.0.0"
```

Validate `/health`, authentication, idea creation, technical approval, persistence, logs, alerts, and restart behavior. Keep the previous image digest available. Roll back by running the same command with the previous immutable tag or digest.

## Production security gates

The following items remain incomplete until implemented and validated with the client:

| Area | Current repository state | Required production control |
|---|---|---|
| Authentication | Demo users; Entra mode returns `501` | Validate Entra access tokens, tenant, audience, issuer, scopes, and app roles |
| Authorization | Three application roles with demo identity | Map Entra app roles/groups and enforce least privilege and tenant isolation server-side |
| Database | SQLite repository | Migrate to PostgreSQL, add schema migrations, pooling, encryption, HA, backup, restore, and DR tests |
| Storage | Managed identity supported with local fallback | Disable local fallback in production, use private Blob access, RBAC, retention, and malware/content validation |
| Secrets | Key Vault foundation exists | Use Key Vault references and managed identity; define rotation and break-glass procedures |
| CORS | Configurable through `AIHUB_ALLOWED_ORIGINS` | Set only approved HTTPS origins; never use `*` with credentials |
| Networking | Public endpoints in the reference foundation | Design VNet integration, private endpoints, private DNS, egress control, WAF/APIM, and administrative access |
| ACR | Admin disabled; public network enabled by default | Use Premium/private endpoint or approved firewall rules, managed identity, Defender scanning, retention, SBOM, and signing |
| API protection | Direct FastAPI ingress | Add APIM or equivalent throttling, quotas, request limits, schema validation, and abuse monitoring |
| Observability | Log Analytics and Application Insights are provisioned | Instrument telemetry, redact sensitive data, define alerts, SLOs, dashboards, and retention |
| Health and scale | `/health` exists; workload probes are not templated | Add probes, replica minimums, autoscaling tests, graceful shutdown, and capacity/load tests |
| Audit and privacy | No complete immutable audit trail | Define audit events, retention, data classification, consent, export, deletion, and incident response |
| Supply chain | Versioned images supported | Pin base images by digest, scan dependencies/images, produce SBOMs, sign images, and enforce deployment policy |
| Responsible AI | Workflow includes human review | Complete impact assessment, human oversight, transparency, evaluation, monitoring, and escalation controls |

Do not set `AIHUB_AUTH_PROVIDER=entra` or claim production readiness until token validation is implemented. Do not connect the current SQLite data layer to a production PostgreSQL endpoint without implementing and testing a PostgreSQL repository and migrations.

## Release evidence

Retain these artifacts for every production release:

- Source commit and pull request approval.
- API and frontend image digests and signatures.
- SBOM and vulnerability scan results.
- Infrastructure deployment record and parameter approval.
- Automated test, security test, load test, backup/restore, and rollback evidence.
- Client security, privacy, compliance, and Responsible AI approvals.
