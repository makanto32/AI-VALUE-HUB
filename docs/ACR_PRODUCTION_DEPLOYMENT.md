# Partner Deployment Guide: Local to Azure Production

This guide takes a delivery partner from local customization to an Azure production baseline. Commands use repository-relative paths only; there are no workstation-specific paths.

## Choose a deployment route

| Route | Use it when | Result |
|---|---|---|
| Local guided validation | The partner needs to customize and test the application first | API and frontend run locally; SQLite is used only for development |
| Deploy to Azure button | The client foundation should be created through Azure Portal | Azure resources, including private PostgreSQL and ACR, are provisioned; no application image is published |
| Azure CLI resource deployment | The client requires a scripted and repeatable foundation deployment | Same foundation as the button, deployed from PowerShell |
| Complete deployment script | The approved code and identity implementation are ready | Foundation, immutable images, API Container App, and frontend Container App are deployed |

> [!IMPORTANT]
> Azure production workloads use `AIHUB_DATABASE_URL` with Azure Database for PostgreSQL. Local evaluation data is not migrated automatically.

> [!WARNING]
> The Azure resources and PostgreSQL adapter are deployable, but client go-live remains blocked until Microsoft Entra ID token validation is implemented and the mandatory controls in this guide pass. `AIHUB_AUTH_PROVIDER=entra` is not currently a working production authentication provider.

## Architecture deployed

```text
Users
  |
  | HTTPS
  v
Frontend Container App
  |
  | HTTPS API calls
  v
API Container App
  |-- Azure Database for PostgreSQL Flexible Server (private access)
  |-- Azure Blob Storage (managed identity; local fallback disabled)
  |-- Azure Key Vault (PostgreSQL connection secret)
  `-- Application Insights and Log Analytics

Both Container Apps pull immutable images from Azure Container Registry by managed identity.
```

## Resources provisioned automatically

The production foundation creates:

- Azure Container Registry with administrator access disabled.
- Virtual network and delegated subnets for Container Apps and PostgreSQL.
- Private DNS zone and VNet link for PostgreSQL.
- Azure Database for PostgreSQL Flexible Server 16 with public network access disabled.
- PostgreSQL database named `aihub`.
- Key Vault and a versioned database connection secret.
- Storage account with private `documents` and `artifacts` containers.
- User-assigned managed identity.
- Container Apps Environment connected to the virtual network.
- Log Analytics Workspace and workspace-based Application Insights.

The workload deployment additionally creates:

- API Container App with PostgreSQL, Blob Storage, telemetry, probes, and HTTPS ingress.
- Frontend Container App with probes and HTTPS ingress.
- `AcrPull`, `Storage Blob Data Contributor`, and `Key Vault Secrets User` assignments.

Custom domains, certificates, Entra app registrations, API Management/WAF, alert rules, budgets, and Defender plans are client-specific and are not created automatically.

## Route 1: customize and validate locally

Use [PARTNER_DEPLOYMENT_GUIDE.md](PARTNER_DEPLOYMENT_GUIDE.md) to customize branding, validation rules, role mapping, languages, and client-specific behavior before creating a release commit. That evaluation environment is separate from the Azure production resources described below.

## Route 2: auto-deploy Azure resources

This route creates the production foundation but does not build or publish application images.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmakanto32%2FAI-VALUE-HUB%2Fmain%2Finfra%2Fazuredeploy.json)

1. Sign in to the client Azure tenant before selecting the button.
2. Select the approved subscription, resource group, and region.
3. Use a short lowercase application name, such as `aivaluehub`.
4. Keep the environment as `prod` unless the client naming standard requires another value.
5. Enter a unique PostgreSQL administrator login and a generated password from the client password vault.
6. Review the template and create the deployment.
7. Save the deployment name and outputs as release evidence.

The password is a secure deployment parameter and is stored in Key Vault as part of the PostgreSQL connection secret. Before go-live, replace administrator use with a least-privilege application database role and rotate the bootstrap credential.

## Route 3: deploy the same resources with Azure CLI

### Prerequisites

- PowerShell 7
- Azure CLI with Bicep support
- Permission to create the resource group resources and role assignments

Authenticate and select the client context:

```powershell
az login --tenant <tenant-id>
az account set --subscription <subscription-id>
az account show --output table
```

Create a secure password in memory and run the resource deployment from the repository root:

```powershell
$postgresPassword = Read-Host "PostgreSQL bootstrap password" -AsSecureString

./infra/deploy-azure-resources.ps1 `
  -SubscriptionId "<subscription-id>" `
  -ResourceGroupName "<resource-group>" `
  -Location "<azure-region>" `
  -AppName "aivaluehub" `
  -EnvironmentName "prod" `
  -PostgresAdminLogin "<bootstrap-admin>" `
  -PostgresAdminPassword $postgresPassword
```

No secret should be written into a parameters file, shell history, source control, or deployment log.

## Publish immutable images after the resources exist

The frontend API URL is compiled into the Vite bundle. Decide the final API hostname before building the frontend image.

The ACR build runs in Azure; Docker is not required on the operator workstation:

```powershell
./infra/push-to-acr.ps1 `
  -ResourceGroupName "<resource-group>" `
  -AcrName "<acr-name-from-deployment-output>" `
  -ApiBaseUrl "https://<approved-api-hostname>" `
  -ImageTag "<release-version-or-git-sha>"
```

The command publishes:

```text
<acr-login-server>/ai-value-hub/api:<immutable-tag>
<acr-login-server>/ai-value-hub/frontend:<immutable-tag>
```

Never use `latest`. Generate an SBOM, scan both images, sign their digests, and promote the approved digests without rebuilding them.

## Integrate the images with Azure resources

The complete script can provision resources, build images in ACR, and deploy both Container Apps:

```powershell
$postgresPassword = Read-Host "PostgreSQL bootstrap password" -AsSecureString

./infra/deploy-production.ps1 `
  -SubscriptionId "<subscription-id>" `
  -ResourceGroupName "<resource-group>" `
  -Location "<azure-region>" `
  -AppName "aivaluehub" `
  -EnvironmentName "prod" `
  -PostgresAdminLogin "<bootstrap-admin>" `
  -PostgresAdminPassword $postgresPassword `
  -ImageTag "<release-version-or-git-sha>" `
  -AuthProvider "demo"
```

`demo` is permitted only for infrastructure validation with synthetic data. Do not onboard client users or data. Change to `entra` only after the API implements and tests Entra JWT validation.

For a client pipeline that already published images, deploy `infra/workloads.bicep` with the immutable API/frontend image references and the outputs from the foundation deployment. Keep Bicep or Terraform as the system of record; do not make undocumented Portal-only production changes.

The API Container App receives:

```text
AIHUB_DATABASE_URL=<Key Vault secret reference to private PostgreSQL>
AIHUB_AUTO_SEED_CONTEXT=false
AIHUB_ENABLE_DEMO_SEED=false
AIHUB_STORAGE_ACCOUNT_NAME=<storage account>
AIHUB_STORAGE_CONTAINER=documents
AIHUB_REQUIRE_CLOUD_STORAGE=true
AIHUB_ALLOWED_ORIGINS=<exact HTTPS frontend origin>
APPLICATIONINSIGHTS_CONNECTION_STRING=<foundation output>
```

Do not add filesystem database or local Blob settings to the production Container App.

## Validate before go-live

The resource deployment is complete only when all relevant checks pass:

1. PostgreSQL public access is disabled; Key Vault, Storage, and ACR network access matches the client-approved baseline.
2. API `/health` and frontend `/` probes are healthy after restart and revision replacement.
3. The API starts with `AIHUB_DATABASE_URL`; no SQLite file or local Blob fallback is used.
4. Confirm the new PostgreSQL database contains no ideas, company context, demo sessions, or sample records. Production sets `AIHUB_AUTO_SEED_CONTEXT=false` and `AIHUB_ENABLE_DEMO_SEED=false`; the demo sample endpoints return `404`.
5. Create, update, retrieve, and delete a synthetic idea; verify persistence after API replica restart.
6. Upload a synthetic context document and verify it exists in the `documents` container.
7. Confirm business users cannot access another user or tenant's records.
8. Confirm ACR administrator access is disabled and Container Apps pull by managed identity.
9. Verify logs contain correlation data but no credentials, tokens, document content, or sensitive prompts.
10. Test backup restore, revision rollback, and database migration rollback in a non-production environment.
11. Record image digests, infrastructure deployment, tests, exceptions, and client approvals.

## Mandatory application work before client production

Infrastructure automation does not remove these application gates:

- Implement Entra access-token validation for signature, issuer, audience, tenant, lifetime, scopes, and app roles.
- Remove demo credentials, local auth sessions, and demo seed behavior.
- Replace automatic schema creation with reviewed, versioned PostgreSQL migrations and a migration job.
- Add PostgreSQL connection pooling, transient-failure handling, least-privilege database roles, and tested backup/restore.
- Complete tenant-isolation, authorization, privacy, threat-model, and Responsible AI testing.

Until these are complete, the deployment is an Azure production-like validation environment, not an approved client production service.

## Delivery 2: security and operational hardening

Plan these items as a second delivery unless client policy requires them before initial go-live:

| Area | Follow-up work |
|---|---|
| Network edge | Custom domains, certificate automation, WAF or Front Door, APIM throttling/quotas, controlled egress |
| Private access | Private endpoints and private DNS for ACR, Storage, and Key Vault; approved administrative access. Move this to Delivery 1 when client policy prohibits public service endpoints. |
| Database resilience | Zone-redundant HA, geo-redundant backup/replica, DR targets and exercises |
| Supply chain | Dependency and image policies, SBOM retention, signing enforcement, admission policy |
| Monitoring | Alert rules, action groups, SLO dashboards, synthetic availability tests, log retention |
| Data protection | Blob lifecycle, backup, malware/content scanning, retention and deletion automation |
| Governance | Azure Policy, Defender for Cloud, budgets, cost alerts, resource locks, naming/tag enforcement |
| Operations | On-call ownership, incident response, credential rotation, break-glass and disaster runbooks |

## Release evidence

Retain for every release:

- Approved source commit and pull request.
- Bicep validation and deployment records.
- API and frontend image digests and signatures.
- SBOM and vulnerability scan results.
- Functional, security, isolation, load, restore, and rollback results.
- Database migration version and rollback procedure.
- Client security, privacy, compliance, operations, and Responsible AI approvals.