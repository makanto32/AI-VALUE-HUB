# Fabric Admin Dashboard Setup Guide

## Overview

This guide provides step-by-step instructions to set up the **Microsoft Fabric workspace and semantic model** required for the AI Value Hub Admin Dashboard to function correctly.

## Prerequisites

Before starting, ensure you have:

- **Azure CLI** installed ([Download](https://aka.ms/azure-cli))
- **Azure account** with Power BI Premium or Fabric capacity
- **Azure subscription** with permissions to create workspaces
- **Admin access** to create or modify Power BI/Fabric workspaces
- API running and accessible (for data sync)

### Verify Prerequisites

```powershell
# Check Azure CLI
az --version

# Login to Azure
az login

# Verify Power BI access
az account show
```

---

## Architecture Overview

The Fabric integration follows a **Medallion Architecture**:

```
┌─────────────────────────────────────────────────────────┐
│                   Admin Dashboard UI                     │
│              (Power BI or Application)                   │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │  Admin Dashboard API  │
         │   (/admin/metrics)    │
         └───────────┬───────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
    ▼                ▼                ▼
┌────────┐     ┌────────┐      ┌──────────┐
│ Local  │     │Semantic│      │Power BI/ │
│Medallion   │Metrics  │      │ Fabric   │
│JSON    │     │File    │      │Dataset   │
└────────┘     └────────┘      └──────────┘
                                   △
                         ┌─────────┴──────────┐
                         │ Workspace: latamdemos│
                         │ Dataset: AIHubSemanticModel│
                         │ Table: DashboardPayload│
                         └────────────────────┘
```

---

## Step 1: Automatic Setup (Recommended)

The easiest way to set up Fabric is using the provided PowerShell script:

### 1.1 Basic Setup

```powershell
cd c:\Projects\AI-OPPORTUNIY-HUB

# Run setup script (creates workspace and semantic model)
.\scripts\fabric-setup-complete.ps1 -WorkspaceName latamdemos
```

**Expected Output:**
```
============================================================================
AI VALUE HUB - FABRIC ADMIN DASHBOARD SETUP
============================================================================

→ Validating prerequisites...
✓ Azure CLI found: ...
✓ Authenticated as: your.email@company.com (Subscription: your-subscription)

→ Looking for workspace 'latamdemos'...
✓ Workspace found: latamdemos (ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)

→ Looking for semantic model 'AIHubSemanticModel' in workspace...
✓ Semantic model found: AIHubSemanticModel (ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)

→ Validating table schema...
✓ Table 'DashboardPayload' exists with 9 columns
```

### 1.2 Setup with Data Sync

To automatically sync initial data from the API:

```powershell
.\scripts\fabric-setup-complete.ps1 -WorkspaceName latamdemos -SyncData
```

This will:
1. Create workspace and semantic model
2. Fetch current dashboard metrics from API
3. Insert data into the DashboardPayload table

### 1.3 Export Configuration

To export environment variables to a file:

```powershell
.\scripts\fabric-setup-complete.ps1 -WorkspaceName latamdemos -ExportConfig
```

This creates `fabric-config.env` with all required variables.

---

## Step 2: Manual Setup (If Needed)

If you prefer manual setup or need to troubleshoot:

### 2.1 Create Workspace

```powershell
$WorkspaceName = "latamdemos"

$workspace = az rest --method post `
  --url "https://api.powerbi.com/v1.0/myorg/groups" `
  --body "{\"name\": \"$WorkspaceName\"}" `
  --output json | ConvertFrom-Json

$WorkspaceId = $workspace.id
Write-Host "Workspace created: $WorkspaceId"
```

### 2.2 Create Semantic Model

```powershell
$DatasetName = "AIHubSemanticModel"
$TableName = "DashboardPayload"

$datasetBody = @{
    name = $DatasetName
    defaultMode = "Push"
    tables = @(
        @{
            name = $TableName
            columns = @(
                @{ name = "tenant_id"; dataType = "string" },
                @{ name = "period"; dataType = "string" },
                @{ name = "generated_at"; dataType = "datetime" },
                @{ name = "payload_json"; dataType = "string" },
                @{ name = "ideas_total"; dataType = "int64" },
                @{ name = "ideas_approved"; dataType = "int64" },
                @{ name = "ideas_rejected"; dataType = "int64" },
                @{ name = "avg_value_score"; dataType = "double" },
                @{ name = "avg_risk_score"; dataType = "double" }
            )
        }
    )
} | ConvertTo-Json -Depth 10

$dataset = az rest --method post `
  --url "https://api.powerbi.com/v1.0/myorg/groups/$WorkspaceId/datasets?defaultRetentionPolicy=basicFIFO" `
  --body $datasetBody `
  --output json | ConvertFrom-Json

$DatasetId = $dataset.id
Write-Host "Dataset created: $DatasetId"
```

### 2.3 Verify Table

```powershell
$table = az rest --method get `
  --url "https://api.powerbi.com/v1.0/myorg/groups/$WorkspaceId/datasets/$DatasetId" `
  --output json | ConvertFrom-Json

$table.tables | Where-Object { $_.name -eq $TableName }
```

---

## Step 3: Configure API Environment Variables

### 3.1 For Local Development

Add to your `.env` or `.env.local`:

```env
# Dashboard metrics source: local | semantic | powerbi
AIHUB_DASHBOARD_METRICS_SOURCE=semantic

# Medallion path (used when AIHUB_DASHBOARD_METRICS_SOURCE=semantic)
AIHUB_SEMANTIC_METRICS_FILE=data/fabric/gold/executive_dashboard_current.json

# Power BI / Fabric IDs (for future native integration)
AIHUB_POWERBI_WORKSPACE_ID=<workspace-id-from-setup>
AIHUB_POWERBI_DATASET_ID=<dataset-id-from-setup>
AIHUB_POWERBI_TABLE_NAME=DashboardPayload
```

### 3.2 For Azure Container Apps

Set environment variables in Azure Portal:

1. Go to your Container App
2. Under **Containers**, click the container name
3. Add environment variables:

| Variable | Value |
|----------|-------|
| `AIHUB_DASHBOARD_METRICS_SOURCE` | `semantic` |
| `AIHUB_SEMANTIC_METRICS_FILE` | `/mnt/data/fabric/gold/executive_dashboard_current.json` |
| `AIHUB_POWERBI_WORKSPACE_ID` | `<workspace-id>` |
| `AIHUB_POWERBI_DATASET_ID` | `<dataset-id>` |
| `AIHUB_POWERBI_TABLE_NAME` | `DashboardPayload` |

---

## Step 4: Sync Dashboard Data

### 4.1 Automated Sync (Recommended)

Use the provided sync script to push dashboard data to Fabric:

```powershell
$WorkspaceId = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
$DatasetId = "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"

.\scripts\fabric-sync-semantic.ps1 `
  -WorkspaceId $WorkspaceId `
  -DatasetId $DatasetId `
  -TableName DashboardPayload `
  -ApiBaseUrl https://aihub-api-dev.yellowwave-f693504a.eastus.azurecontainerapps.io `
  -AdminUser admin.valuehub `
  -AdminPassword Demo1234!
```

### 4.2 Automated Sync via API Endpoint

The API includes an endpoint to refresh the Medallion pipeline:

```powershell
$token = "your-demo-bearer-token"

curl -X POST https://your-api/admin/metrics/semantic/refresh `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json"
```

### 4.3 Schedule Recurring Sync

Create a Windows Task Scheduler job to sync every hour:

```powershell
$taskName = "AIHub-Fabric-Dashboard-Sync"
$taskPath = "C:\Projects\AI-OPPORTUNIY-HUB\scripts\fabric-sync-semantic.ps1"
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
  -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$taskPath`" -WorkspaceId $WorkspaceId -DatasetId $DatasetId"
$trigger = New-ScheduledTaskTrigger -Hourly -At 00:00
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger
```

---

## Step 5: Verify Setup

### 5.1 Check Medallion Files

```bash
# Verify Medallion artifacts were generated
ls -la data/fabric/bronze/
ls -la data/fabric/silver/
ls -la data/fabric/gold/

# Check dashboard metrics file
cat data/fabric/gold/executive_dashboard_current.json
```

### 5.2 Check Power BI/Fabric Workspace

1. Go to [Power BI / Fabric](https://app.powerbi.com/)
2. Navigate to **Workspaces** → **latamdemos**
3. Verify **AIHubSemanticModel** dataset exists
4. Open the semantic model → **DashboardPayload** table
5. Verify data is present (should see 1 row after sync)

### 5.3 Test Admin Dashboard API

```powershell
# Get authentication token
$auth = curl -X POST https://your-api/auth/login `
  -H "Content-Type: application/json" `
  -d '{"username":"admin.valuehub","password":"Demo1234!"}'

$token = $auth.access_token

# Fetch dashboard snapshot
curl -X GET https://your-api/admin/metrics/executive-dashboard/snapshot?period=current `
  -H "Authorization: Bearer $token"
```

### 5.4 Test Admin Dashboard UI

1. Navigate to application URL
2. Login as **admin.valuehub** / **Demo1234!**
3. Go to **Admin Dashboard** section
4. Verify metrics display correctly:
   - Total ideas
   - Approved ideas
   - Rejected ideas
   - Average scores
   - KPIs

---

## Troubleshooting

### Issue: "No Fabric capacity found"

**Cause:** Workspace doesn't have Fabric or Power BI Premium capacity assigned.

**Solution:**
1. Go to [Power BI Admin Portal](https://app.powerbi.com/admin-portal/capacities)
2. Assign capacity to workspace or create new capacity

### Issue: "Authentication failed"

**Cause:** Azure CLI not authenticated or token expired.

**Solution:**
```powershell
az login
# or force re-authentication
az login --allow-no-subscriptions --force
```

### Issue: "Dataset not found" after creation

**Cause:** API call completed but dataset still initializing.

**Solution:** Wait 30-60 seconds and try again:
```powershell
Start-Sleep -Seconds 60
.\scripts\fabric-setup-complete.ps1 -WorkspaceName latamdemos
```

### Issue: "Data sync fails with 400 error"

**Cause:** API credentials incorrect or API endpoint unreachable.

**Solution:**
1. Verify API is running and accessible
2. Check credentials (admin.valuehub / Demo1234!)
3. Verify network connectivity:
   ```powershell
   Test-NetConnection -ComputerName api-host -Port 443
   ```

### Issue: Dashboard shows "No data available"

**Cause:** Data hasn't been synced to Fabric semantic model.

**Solution:**
1. Run data sync manually:
   ```powershell
   .\scripts\fabric-sync-semantic.ps1 -WorkspaceId $WorkspaceId -DatasetId $DatasetId
   ```
2. Verify data in Power BI workspace: **AIHubSemanticModel** → **DashboardPayload**

---

## Advanced Configuration

### Power BI / Fabric Native Integration

For future native Power BI/Fabric integration (reading directly from semantic model):

1. Register application in Azure AD
2. Get credentials:
   - Tenant ID
   - Client ID
   - Client Secret
   
3. Configure environment variables:
   ```env
   AIHUB_DASHBOARD_METRICS_SOURCE=powerbi
   AIHUB_POWERBI_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   AIHUB_POWERBI_CLIENT_ID=yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy
   AIHUB_POWERBI_CLIENT_SECRET=your-secret-here
   AIHUB_POWERBI_WORKSPACE_ID=<workspace-id>
   AIHUB_POWERBI_DATASET_ID=<dataset-id>
   AIHUB_POWERBI_TABLE_NAME=DashboardPayload
   ```

### Custom Medallion Pipeline

To customize the Medallion data transformation:

1. Edit `api/app/fabric_medallion.py`
2. Modify Bronze → Silver → Gold transformations
3. Run pipeline:
   ```powershell
   python scripts/build-fabric-medallion.py
   ```

---

## Data Flow Diagram

```
┌──────────────────────┐
│  API Database        │
│  (SQLite/PostgreSQL) │
└──────────┬───────────┘
           │
           │ (api/app/fabric_medallion.py)
           ▼
    ┌──────────────────┐
    │  BRONZE LAYER    │
    │ ideas_raw.jsonl  │
    └────────┬─────────┘
             │
             │ (Validate, normalize)
             ▼
    ┌──────────────────┐
    │  SILVER LAYER    │
    │ ideas_clean.csv  │
    └────────┬─────────┘
             │
             │ (Aggregate, calculate KPIs)
             ▼
    ┌───────────────────────────────────────┐
    │  GOLD LAYER                           │
    │ ├─ executive_dashboard_current.json   │
    │ └─ fact_dashboard_kpis.csv            │
    └───────────┬─────────────────────────────┘
                │
      ┌─────────┴──────────┐
      │                    │
      ▼                    ▼
 ┌─────────────┐    ┌────────────────┐
 │  Dashboard  │    │ Fabric/PowerBI │
 │  (Semantic) │    │   Dataset      │
 │   Local     │    │  (Push mode)   │
 └─────────────┘    └────────────────┘
      │                    │
      └────────┬───────────┘
               │
               ▼
        ┌───────────────┐
        │ Admin UI      │
        │ (Dashboard)   │
        └───────────────┘
```

---

## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `fabric-setup-complete.ps1` | End-to-end setup | `.\scripts\fabric-setup-complete.ps1 -WorkspaceName latamdemos` |
| `fabric-sync-semantic.ps1` | Sync data to Fabric | `.\scripts\fabric-sync-semantic.ps1 -WorkspaceId <id> -DatasetId <id>` |
| `fabric-provision-semantic.ps1` | Create semantic model | `.\scripts\fabric-provision-semantic.ps1 -WorkspaceName latamdemos` |
| `build-fabric-medallion.py` | Build Medallion pipeline | `python scripts/build-fabric-medallion.py` |

---

## Next Steps

1. ✅ Run `fabric-setup-complete.ps1` to create workspace and semantic model
2. ✅ Verify setup in Power BI/Fabric workspace
3. ✅ Configure API environment variables
4. ✅ Sync initial data using `fabric-sync-semantic.ps1`
5. ✅ Test Admin Dashboard UI
6. ✅ Schedule recurring data sync
7. ✅ Monitor dashboard metrics regularly

---

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review API logs: `/admin/metrics/debug`
3. Verify Fabric table schema: Power BI Admin Portal
4. Check data freshness: Dashboard → Refresh metadata

---

**Version:** 1.0  
**Last Updated:** February 14, 2026  
**Status:** Production Ready
