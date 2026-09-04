# ACR and Client Production Deployment Guide

This runbook guides a delivery partner from an approved AI Value Hub revision to a controlled client deployment on Azure. It separates mandatory production work from a second delivery of advanced security, resilience, and operations.

> **Production blocker:** the repository is suitable for demo/evaluation but is not production-ready as-is. Entra ID token validation and a PostgreSQL persistence implementation must be completed and tested before client users or data are onboarded. `AIHUB_AUTH_PROVIDER=entra` currently returns `501`; enabling the Bicep PostgreSQL resource does not migrate the SQLite repository.

## Target architecture

```text
Users -> HTTPS frontend Container App (nginx:80)
      -> HTTPS API Container App (FastAPI:8000)
         |-- Microsoft Entra ID
         |-- PostgreSQL Flexible Server
         |-- Azure Blob Storage
         |-- Key Vault
         `-- Application Insights / Log Analytics

Both Container Apps pull signed, immutable images from ACR using managed identity.
```

The frontend API URL is embedded during the Vite build. Approve the production API hostname before building the frontend image.

## Resource inventory

### Created by `infra/main.bicep`

| Resource | Current template | Production decision |
|---|---|---|
| Log Analytics Workspace | Created, 30-day retention | Set client retention policy |
| Application Insights | Workspace-based | Add instrumentation, alerts, dashboards |
| Storage Account | Standard LRS, TLS 1.2 | Select redundancy and network isolation |
| Blob containers | `documents`, `artifacts`; private | Add lifecycle, retention, backup, malware scanning |
| ACR | Optional Standard; admin disabled | Use Premium for private endpoint/geo-replication |
| User Assigned Managed Identity | Created | Assign minimum data-plane roles |
| Key Vault | RBAC, 90-day soft delete | Add purge protection and network controls |
| Container Apps Environment | Consumption profile | Configure approved network/zone design |
| PostgreSQL Flexible Server | Optional; disabled | Enable only after application migration |

The deployment script also creates or updates the resource group.

### Added by the client platform pipeline

The current foundation does **not** create:

- API and frontend Container Apps.
- Ingress, custom domains, TLS certificates, probes, scaling, or revision policy.
- DNS records and certificate automation.
- Entra app registrations, application roles, and assignments.
- PostgreSQL database/schema, migrations, or application database identity.
- RBAC assignments for ACR, Blob, Key Vault, and PostgreSQL.
- Alerts, action groups, dashboards, budgets, or Defender plans.
- Private endpoints/DNS, VNet integration, APIM, or WAF.

Add these resources to approved client IaC. Portal-only production changes must not become the system of record.

## Delivery 1: mandatory production launch controls

Every control is required before go-live unless the client's security authority records a time-bound exception and compensating control.

1. **Identity and authorization:** validate Entra JWT signature, issuer, audience, tenant, lifetime, scopes, and app roles. Map business, technical, and administrator roles. Enforce tenant/object authorization in the API. Remove demo identities and sessions.
2. **Persistence:** replace SQLite/`AIHUB_DB_PATH` with a PostgreSQL repository. Add migrations, pooling, transient-failure handling, encryption, HA, backup, restore, and rollback tests.
3. **File storage:** use Blob through managed identity; disable local/connection-string fallback. Add type, size, content, malware, retention, and deletion controls.
4. **Network and edge:** use approved HTTPS domains and exact CORS origins. Define ingress, egress, DNS, and administration. Add APIM/WAF/private networking when required by policy or threat model.
5. **Secrets:** use managed identity or Key Vault references. Define rotation, expiry alerts, revocation, and break-glass procedures.
6. **Reliability:** configure probes, CPU/memory, replica bounds, autoscaling, graceful shutdown, immutable revisions, and rollback.
7. **Observability/audit:** instrument telemetry without sensitive payloads. Alert on availability, errors, latency, identity failures, dependencies, capacity, and expiry. Audit actor, tenant, action, target, result, and correlation ID.
8. **Supply chain:** protect branches, review releases, pin dependencies/base images, generate SBOMs, scan code/images/IaC, sign digests, and promote the same approved digest.
9. **Governance:** complete threat model, data classification, privacy/compliance, tenant isolation, retention/deletion, and Responsible AI assessments.
10. **Acceptance:** pass functional, authorization, isolation, security, performance, restore, failover, and rollback tests; obtain application, platform, security, compliance, and operations approval.

## Prerequisites

- Azure CLI authenticated to the client tenant/subscription.
- Contributor on the deployment resource group.
- ACR build/push and role-assignment permissions.
- Approved region, names, domains, certificates, API/frontend URLs, RPO, and RTO.
- A clean, reviewed, tested release commit.

```powershell
az login --tenant <tenant-id>
az account set --subscription <subscription-id>
az account show --output table
```

## 1. Prepare production parameters

The checked-in parameters enable ACR, disable PostgreSQL, and use `environmentName=dev`. Do not reuse them unchanged. Approve subscription, tenant, region, names, environment, tags/cost center, ACR SKU, storage redundancy, log retention, database tier/HA/backup, URLs, RPO, and RTO. Keep sensitive values outside source control.

## 2. Deploy the Azure foundation

Review `infra/main.bicep` and the production parameter file, then run from the repository root:

```powershell
.\infra\deploy-foundation.ps1 `
  -ResourceGroupName "rg-ai-value-hub-prod" `
  -Location "eastus" `
  -TemplateFile ".\infra\main.bicep" `
  -ParametersFile ".\infra\main.parameters.json"
```

Capture and protect the ACR login server, identity IDs, Key Vault name, Storage name, Container Apps Environment ID, and Application Insights connection string.

## 3. Publish immutable OCI images

```powershell
.\infra\push-to-acr.ps1 `
  -ResourceGroupName "rg-ai-value-hub-prod" `
  -AcrName "<acr-name>" `
  -ApiBaseUrl "https://api.valuehub.contoso.com" `
  -ImageTag "1.0.0"
```

```text
<acr>.azurecr.io/ai-value-hub/api:<tag>
<acr>.azurecr.io/ai-value-hub/frontend:<tag>
```

The script rejects `latest`. Retain digests, scans, SBOMs, signatures, source commit, and pipeline run. Promote approved digests instead of rebuilding.

## 4. Assign least privilege

```powershell
$acrId = az acr show --name "<acr-name>" --query id --output tsv
$principalId = az identity show `
  --resource-group "rg-ai-value-hub-prod" `
  --name "<managed-identity-name>" `
  --query principalId --output tsv
az role assignment create `
  --assignee-object-id $principalId `
  --assignee-principal-type ServicePrincipal `
  --role AcrPull `
  --scope $acrId
```

Assign only required Blob, Key Vault, and database permissions at narrow scope in IaC. Keep ACR admin disabled.

## 5. Create and configure workloads

| Setting | API | Frontend |
|---|---|---|
| Image | Approved API digest | Digest built with production API URL |
| Port | `8000` | `80` |
| Ingress | Approved API design | External HTTPS |
| Probe | `/health` | `/` |
| Registry | Managed identity | Managed identity |
| Revision mode | Multiple for controlled rollback | Client policy |
| Scale | Tested min/max and HTTP/concurrency | Tested min/max and HTTP/concurrency |

Do not use `AIHUB_AUTH_PROVIDER=demo`, `AIHUB_DB_PATH`, or `AIHUB_LOCAL_BLOB_ROOT` in production. Use configuration introduced by the completed Entra/PostgreSQL adapters. Current supported storage/CORS values include:

```text
AIHUB_STORAGE_ACCOUNT_NAME=<storage-account>
AIHUB_STORAGE_CONTAINER=documents
AIHUB_ALLOWED_ORIGINS=https://valuehub.contoso.com
APPLICATIONINSIGHTS_CONNECTION_STRING=<Key Vault reference or protected setting>
```

Disable automatic demo seeding. Keep secrets out of source, images, parameter files, pipeline output, and plain settings.

## 6. Configure identity, DNS, TLS, and edge

Register frontend/API in Entra, define roles and assignment ownership, bind client domains, validate certificate renewal, enforce HTTPS/exact CORS, and confirm browsers reach the embedded API URL. Apply APIM, WAF, private connectivity, and request/rate limits required by the approved design.

## 7. Deploy an approved release

```powershell
$loginServer = az acr show --name "<acr-name>" --query loginServer --output tsv
.\infra\update-container-apps.ps1 `
  -ResourceGroupName "rg-ai-value-hub-prod" `
  -ApiContainerAppName "ai-value-hub-prod-api" `
  -ApiImage "$loginServer/ai-value-hub/api:1.0.0" `
  -FrontendContainerAppName "ai-value-hub-prod-frontend" `
  -FrontendImage "$loginServer/ai-value-hub/frontend:1.0.0" `
  -RevisionSuffix "v100"
```

Deploy first to production-like staging, then promote the same approved digests.

## 8. Validate before traffic

- API `/health` and frontend `/` through intended routes.
- Entra login, expiry, invalid issuer/audience, disabled users, role changes.
- Business/reviewer/admin, owner, and tenant API authorization.
- Full workflow and file handling across restart and scale-out.
- Migrations, backup/restore, Blob retention/deletion, dependency failure.
- HTTPS, CORS, DNS, certificates, ingress/egress, edge policies.
- Telemetry redaction/correlation, alerts, dashboards, load, scaling, rollback.
- Residual risks have owner, control, and expiry date.

## 9. Release and rollback

Record revisions, traffic weights, migration/configuration versions, and image digests. Use canary or blue/green progression when required. Roll back traffic to the previous healthy revision or signed digest. Database changes need forward compatibility or a separately tested rollback; reverting only the image can be unsafe.

## Current implementation gaps

| Area | Current state | Production control |
|---|---|---|
| Authentication | Demo; Entra returns `501` | Token validation and role mapping |
| Authorization | Demo identity roles | Least privilege and tenant isolation |
| Database | SQLite | PostgreSQL adapter, migrations, pooling, HA, restore |
| Storage | Local fallback exists | Managed identity, private Blob, content controls |
| Secrets | Key Vault foundation | References, identity, rotation |
| Network | Public reference | Approved private/egress/edge design |
| ACR | Public by default | Firewall/private access, scans, signing |
| API | Direct FastAPI | Throttling, quotas, payload/schema limits |
| Observability | Platform resources | Instrumentation, redaction, alerts, SLOs |
| Audit/privacy | Incomplete trail | Events, retention, classification, data rights |
| Supply chain | Versioned images | Pins, SBOM, scans, signatures, policy |
| Responsible AI | Human review | Assessment, evaluation, monitoring, escalation |

## Delivery 2: security and platform backlog

A threat model, regulation, classification, or availability requirement can move any item into Delivery 1.

| Workstream | Candidate capabilities | Exit evidence |
|---|---|---|
| Network isolation | VNet environment, private endpoints/DNS, controlled egress | Diagram and exfiltration tests |
| API edge | APIM, WAF, quotas, schema/payload/bot controls | Policy tests and alerts |
| Advanced identity | Conditional Access, PIM/JIT, access reviews, federation | Access certification |
| Resilience/DR | Zones, PostgreSQL HA, geo-backup, second region | RTO/RPO exercise |
| Security operations | Defender, Sentinel, detections/playbooks, audit archive | Incident simulation |
| Supply chain | Private agents, provenance, signed-image admission | Policy denial tests |
| Data governance | Purview, DLP, CMK if required, legal hold, data requests | Lifecycle tests |
| Responsible AI | Quality/safety and outcome monitoring, appeal/review | Approved metrics/reports |
| Performance/cost | Load tuning, capacity, budgets, anomaly alerts | Capacity/cost baseline |
| Operations | SLO/error budgets, synthetic/chaos tests, patch cadence | Operational acceptance |
| Analytics | Fabric/Power BI identity, private paths, RLS, lineage | Access/refresh tests |

## Production acceptance checklist

- [ ] Entra token and server-side role/tenant authorization tested.
- [ ] Demo credentials/authentication/seeding disabled.
- [ ] PostgreSQL adapter/migrations and restore proven.
- [ ] Blob uses managed identity and approved content controls.
- [ ] HTTPS, CORS, DNS, certificates, and edge controls validated.
- [ ] Secrets and rotation ownership approved.
- [ ] Probes, scaling, revisions, and graceful failure tested.
- [ ] Telemetry, audit, alerts, dashboards, on-call operational.
- [ ] Images immutable, scanned, signed, and approved by digest.
- [ ] Security, privacy, governance, and Responsible AI approved.
- [ ] Performance, restore, DR, and rollback evidence retained.
- [ ] Runbooks, ownership, SLOs, risks, and exceptions approved.

## Release evidence

Retain source/PR approvals, IaC deployment records, approved parameters, image digests/signatures/SBOM/scans, migration and restore evidence, test results, active revisions/traffic/configuration, change record, and client application/platform/security/compliance/Responsible AI/operations approvals.

## Scope and ownership

The repository supplies a reference application, Dockerfiles, publication/update scripts, and a partial Azure foundation. The partner owns client production architecture, IaC completion, application remediation, testing, migration, operations, and evidence. The client owns risk acceptance, policy, governance, compliance, availability objectives, and go-live approval.
