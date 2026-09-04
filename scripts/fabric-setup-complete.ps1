#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Complete Fabric workspace and semantic model setup for AI Value Hub Admin Dashboard
    
.DESCRIPTION
    This script automates the entire Fabric/Power BI setup required for the admin dashboard:
    1. Validates prerequisites (Azure CLI, authentication)
    2. Creates or locates the Fabric workspace
    3. Creates the semantic model with proper schema
    4. Sets up the DashboardPayload table
    5. Provides environment variables for API configuration
    6. Optionally syncs initial data from the API
    
.PARAMETER WorkspaceName
    Name of the Fabric workspace (default: latamdemos)
    
.PARAMETER DatasetName
    Name of the semantic model dataset (default: AIHubSemanticModel)
    
.PARAMETER TableName
    Name of the dashboard payload table (default: DashboardPayload)
    
.PARAMETER ApiBaseUrl
    Base URL of the AI Hub API for syncing data
    
.PARAMETER AdminUser
    Admin username for API authentication
    
.PARAMETER AdminPassword
    Admin password for API authentication
    
.PARAMETER SyncData
    If specified, syncs initial data from API after setup
    
.EXAMPLE
    .\fabric-setup-complete.ps1 -WorkspaceName latamdemos
    
.EXAMPLE
    .\fabric-setup-complete.ps1 -WorkspaceName latamdemos -SyncData
    
.NOTES
    Prerequisites:
    - Azure CLI (az) must be installed
    - Must be authenticated with 'az login'
    - Must have Power BI Premium capacity or Fabric capacity
    - Must have Fabric admin or member role in target workspace
#>

param(
    [Parameter(Mandatory = $false)]
    [string]$WorkspaceName = "latamdemos",

    [Parameter(Mandatory = $false)]
    [string]$DatasetName = "AIHubSemanticModel",

    [Parameter(Mandatory = $false)]
    [string]$TableName = "DashboardPayload",
    
    [Parameter(Mandatory = $false)]
    [string]$ApiBaseUrl = "https://aihub-api-dev.yellowwave-f693504a.eastus.azurecontainerapps.io",
    
    [Parameter(Mandatory = $false)]
    [string]$AdminUser = "admin.valuehub",
    
    [Parameter(Mandatory = $false)]
    [string]$AdminPassword = "Demo1234!",
    
    [Parameter(Mandatory = $false)]
    [switch]$SyncData = $false,
    
    [Parameter(Mandatory = $false)]
    [switch]$ExportConfig = $false
)

$ErrorActionPreference = "Stop"
$WarningPreference = "Continue"

# Color configuration
$InfoColor = "Cyan"
$SuccessColor = "Green"
$WarningColor = "Yellow"
$ErrorColor = "Red"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

function Write-Title {
    param([string]$Message)
    Write-Host "`n$('=' * 70)" -ForegroundColor $InfoColor
    Write-Host $Message -ForegroundColor $InfoColor
    Write-Host $('=' * 70) -ForegroundColor $InfoColor
}

function Write-Step {
    param([string]$Message)
    Write-Host "`n→ $Message" -ForegroundColor $InfoColor
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor $SuccessColor
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor $WarningColor
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor $ErrorColor
    throw $Message
}

function Test-Prerequisites {
    Write-Step "Validating prerequisites..."
    
    # Check Azure CLI
    $azVersion = az --version 2>&1 | Select-Object -First 1
    if (-not $azVersion) {
        Write-Error "Azure CLI is not installed. Please install it from https://aka.ms/azure-cli"
    }
    Write-Success "Azure CLI found: $azVersion"
    
    # Check Azure authentication
    $currentAccount = az account show 2>&1 | ConvertFrom-Json
    if (-not $currentAccount.id) {
        Write-Error "Not authenticated with Azure. Please run 'az login' first"
    }
    Write-Success "Authenticated as: $($currentAccount.user.name) (Subscription: $($currentAccount.name))"
}

function Get-PowerBIToken {
    try {
        $tokenJson = az account get-access-token --resource https://analysis.windows.net/powerbi/api --output json 2>&1 | ConvertFrom-Json
        if (-not $tokenJson.accessToken) {
            throw "No access token returned"
        }
        return $tokenJson.accessToken
    }
    catch {
        Write-Error "Failed to obtain Power BI/Fabric API token: $_"
    }
}

function Invoke-FabricApi {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Method,
        
        [Parameter(Mandatory = $true)]
        [string]$Path,
        
        [Parameter(Mandatory = $false)]
        [object]$Body = $null,
        
        [Parameter(Mandatory = $false)]
        [int]$RetryCount = 3
    )
    
    $token = Get-PowerBIToken
    $uri = "https://api.powerbi.com/v1.0/myorg/$Path"
    $headers = @{ Authorization = "Bearer $token" }
    
    $attempt = 0
    $lastError = $null
    
    while ($attempt -lt $RetryCount) {
        try {
            if ($null -eq $Body) {
                return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers -TimeoutSec 60
            }
            else {
                return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers `
                    -ContentType "application/json" -Body ($Body | ConvertTo-Json -Depth 30) -TimeoutSec 60
            }
        }
        catch {
            $lastError = $_
            $attempt++
            if ($attempt -lt $RetryCount) {
                Write-Warning "API call failed (attempt $attempt/$RetryCount): $($_.Exception.Message)"
                Start-Sleep -Seconds (2 * $attempt)
            }
        }
    }
    
    Write-Error "API call failed after $RetryCount attempts: $lastError"
}

function Get-Or-Create-Workspace {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name
    )
    
    Write-Step "Looking for workspace '$Name'..."
    
    try {
        $groups = Invoke-FabricApi -Method GET -Path "groups"
        $workspace = $groups.value | Where-Object { $_.name -eq $Name } | Select-Object -First 1
        
        if ($workspace) {
            Write-Success "Workspace found: $Name (ID: $($workspace.id))"
            return $workspace
        }
        else {
            Write-Warning "Workspace not found. Creating workspace '$Name'..."
            
            # Create new workspace
            $createBody = @{
                name = $Name
            }
            
            $newWorkspace = Invoke-FabricApi -Method POST -Path "groups" -Body $createBody
            Write-Success "Workspace created: $Name (ID: $($newWorkspace.id))"
            return $newWorkspace
        }
    }
    catch {
        Write-Error "Failed to get or create workspace: $_"
    }
}

function Get-Or-Create-Dataset {
    param(
        [Parameter(Mandatory = $true)]
        [string]$WorkspaceId,
        
        [Parameter(Mandatory = $true)]
        [string]$DatasetName,
        
        [Parameter(Mandatory = $true)]
        [string]$TableName
    )
    
    Write-Step "Looking for semantic model '$DatasetName' in workspace..."
    
    try {
        $datasets = Invoke-FabricApi -Method GET -Path "groups/$WorkspaceId/datasets"
        $dataset = $datasets.value | Where-Object { $_.name -eq $DatasetName } | Select-Object -First 1
        
        if ($dataset) {
            Write-Success "Semantic model found: $DatasetName (ID: $($dataset.id))"
            return $dataset
        }
        else {
            Write-Step "Semantic model not found. Creating '$DatasetName'..."
            
            # Create new dataset with Push mode
            $createBody = @{
                name = $DatasetName
                defaultMode = "Push"
                tables = @(
                    @{
                        name = $TableName
                        columns = @(
                            @{ 
                                name = "tenant_id"
                                dataType = "string"
                            },
                            @{ 
                                name = "period"
                                dataType = "string"
                            },
                            @{ 
                                name = "generated_at"
                                dataType = "datetime"
                            },
                            @{ 
                                name = "payload_json"
                                dataType = "string"
                            },
                            @{ 
                                name = "ideas_total"
                                dataType = "int64"
                            },
                            @{ 
                                name = "ideas_approved"
                                dataType = "int64"
                            },
                            @{ 
                                name = "ideas_rejected"
                                dataType = "int64"
                            },
                            @{ 
                                name = "avg_value_score"
                                dataType = "double"
                            },
                            @{ 
                                name = "avg_risk_score"
                                dataType = "double"
                            }
                        )
                    }
                )
            }
            
            $newDataset = Invoke-FabricApi -Method POST -Path "groups/$WorkspaceId/datasets?defaultRetentionPolicy=basicFIFO" -Body $createBody
            Write-Success "Semantic model created: $DatasetName (ID: $($newDataset.id))"
            return $newDataset
        }
    }
    catch {
        Write-Error "Failed to get or create semantic model: $_"
    }
}

function Test-DatasetTable {
    param(
        [Parameter(Mandatory = $true)]
        [string]$WorkspaceId,
        
        [Parameter(Mandatory = $true)]
        [string]$DatasetId,
        
        [Parameter(Mandatory = $true)]
        [string]$TableName
    )
    
    Write-Step "Validating table schema..."
    
    try {
        $dataset = Invoke-FabricApi -Method GET -Path "groups/$WorkspaceId/datasets/$DatasetId"
        $table = $dataset.tables | Where-Object { $_.name -eq $TableName } | Select-Object -First 1
        
        if ($table) {
            Write-Success "Table '$TableName' exists with $($table.columns.Count) columns"
            return $true
        }
        else {
            Write-Warning "Table '$TableName' not found in dataset"
            return $false
        }
    }
    catch {
        Write-Error "Failed to validate table: $_"
    }
}

function Sync-DataFromApi {
    param(
        [Parameter(Mandatory = $true)]
        [string]$WorkspaceId,
        
        [Parameter(Mandatory = $true)]
        [string]$DatasetId,
        
        [Parameter(Mandatory = $true)]
        [string]$TableName,
        
        [Parameter(Mandatory = $false)]
        [string]$ApiUrl = "https://aihub-api-dev.yellowwave-f693504a.eastus.azurecontainerapps.io",
        
        [Parameter(Mandatory = $false)]
        [string]$User = "admin.valuehub",
        
        [Parameter(Mandatory = $false)]
        [string]$Password = "Demo1234!"
    )
    
    Write-Step "Syncing data from API..."
    
    try {
        # Authenticate with API
        Write-Step "Authenticating with API..."
        $loginBody = @{ username = $User; password = $Password } | ConvertTo-Json
        $auth = Invoke-RestMethod -Method Post -Uri "$ApiUrl/auth/login" `
            -ContentType "application/json" -Body $loginBody -TimeoutSec 30
        
        if (-not $auth.access_token) {
            throw "API authentication failed"
        }
        Write-Success "API authentication successful"
        
        # Get dashboard snapshot
        Write-Step "Fetching dashboard snapshot from API..."
        $apiHeaders = @{ Authorization = "Bearer $($auth.access_token)" }
        $dashboard = Invoke-RestMethod -Method Get `
            -Uri "$ApiUrl/admin/metrics/executive-dashboard/snapshot?period=current" `
            -Headers $apiHeaders -TimeoutSec 30
        
        Write-Success "Dashboard snapshot retrieved"
        
        # Prepare payload
        $tenantId = "default"
        $generatedAt = (Get-Date).ToUniversalTime().ToString("o")
        $payloadJson = $dashboard | ConvertTo-Json -Depth 50 -Compress
        
        # Clear existing rows
        Write-Step "Clearing existing data from table..."
        Invoke-FabricApi -Method DELETE -Path "groups/$WorkspaceId/datasets/$DatasetId/tables/$TableName/rows"
        Write-Success "Table cleared"
        
        # Insert new data
        Write-Step "Inserting dashboard data into table..."
        $rowsBody = @{
            rows = @(
                @{
                    tenant_id = $tenantId
                    period = "current"
                    generated_at = $generatedAt
                    payload_json = $payloadJson
                    ideas_total = $dashboard.ideas.total
                    ideas_approved = $dashboard.ideas.approved
                    ideas_rejected = $dashboard.ideas.rejected
                    avg_value_score = $dashboard.metrics.avg_value_score
                    avg_risk_score = $dashboard.metrics.avg_risk_score
                }
            )
        }
        
        Invoke-FabricApi -Method POST `
            -Path "groups/$WorkspaceId/datasets/$DatasetId/tables/$TableName/rows" `
            -Body $rowsBody
        
        Write-Success "Data synced successfully"
    }
    catch {
        Write-Error "Failed to sync data: $_"
    }
}

function Export-EnvironmentVariables {
    param(
        [Parameter(Mandatory = $true)]
        [string]$WorkspaceId,
        
        [Parameter(Mandatory = $true)]
        [string]$DatasetId,
        
        [Parameter(Mandatory = $true)]
        [string]$TableName
    )
    
    $envContent = @"
# AI Value Hub - Fabric Admin Dashboard Configuration
# Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

# Dashboard metrics source: local (Medallion), semantic (local JSON), or powerbi (Fabric API)
AIHUB_DASHBOARD_METRICS_SOURCE=semantic

# Semantic model metrics file path (used when AIHUB_DASHBOARD_METRICS_SOURCE=semantic)
AIHUB_SEMANTIC_METRICS_FILE=/mnt/data/fabric/gold/executive_dashboard_current.json

# Power BI / Fabric Integration (used when AIHUB_DASHBOARD_METRICS_SOURCE=powerbi)
AIHUB_POWERBI_WORKSPACE_ID=$WorkspaceId
AIHUB_POWERBI_DATASET_ID=$DatasetId
AIHUB_POWERBI_TABLE_NAME=$TableName

# Note: For full Power BI/Fabric integration, also configure:
# - AIHUB_POWERBI_TENANT_ID (from Azure AD)
# - AIHUB_POWERBI_CLIENT_ID (registered app)
# - AIHUB_POWERBI_CLIENT_SECRET (app secret)
"@

    return $envContent
}

function Export-SetupSummary {
    param(
        [Parameter(Mandatory = $true)]
        [string]$WorkspaceName,
        
        [Parameter(Mandatory = $true)]
        [string]$WorkspaceId,
        
        [Parameter(Mandatory = $true)]
        [string]$DatasetName,
        
        [Parameter(Mandatory = $true)]
        [string]$DatasetId,
        
        [Parameter(Mandatory = $true)]
        [string]$TableName
    )
    
    Write-Title "FABRIC SETUP COMPLETE - CONFIGURATION SUMMARY"
    
    $summary = [ordered]@{
        "Workspace Name" = $WorkspaceName
        "Workspace ID" = $WorkspaceId
        "Dataset Name" = $DatasetName
        "Dataset ID" = $DatasetId
        "Table Name" = $TableName
        "Setup Date" = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        "PowerBI API Base" = "https://api.powerbi.com/v1.0/myorg"
    }
    
    Write-Host ""
    $summary.GetEnumerator() | ForEach-Object {
        Write-Host "$($_.Key):".PadRight(25) -ForegroundColor $InfoColor -NoNewline
        Write-Host $_.Value -ForegroundColor $SuccessColor
    }
    
    Write-Host ""
    Write-Success "Configuration exported successfully!"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

function Main {
    Write-Title "AI VALUE HUB - FABRIC ADMIN DASHBOARD SETUP"
    
    try {
        # Step 1: Validate prerequisites
        Test-Prerequisites
        
        # Step 2: Get or create workspace
        $workspace = Get-Or-Create-Workspace -Name $WorkspaceName
        $workspaceId = $workspace.id
        
        # Step 3: Get or create semantic model
        $dataset = Get-Or-Create-Dataset -WorkspaceId $workspaceId -DatasetName $DatasetName -TableName $TableName
        $datasetId = $dataset.id
        
        # Step 4: Validate table schema
        $tableValid = Test-DatasetTable -WorkspaceId $workspaceId -DatasetId $datasetId -TableName $TableName
        
        if (-not $tableValid) {
            Write-Warning "Table validation failed. You may need to manually recreate the semantic model."
        }
        
        # Step 5: Sync data from API if requested
        if ($SyncData) {
            Write-Step "Data synchronization requested"
            Sync-DataFromApi -WorkspaceId $workspaceId -DatasetId $datasetId -TableName $TableName `
                -ApiUrl $ApiBaseUrl -User $AdminUser -Password $AdminPassword
        }
        else {
            Write-Warning "Data synchronization skipped. Run 'scripts/fabric-sync-semantic.ps1' manually or specify -SyncData flag"
        }
        
        # Step 6: Export configuration
        $envVars = Export-EnvironmentVariables -WorkspaceId $workspaceId -DatasetId $datasetId -TableName $TableName
        
        if ($ExportConfig) {
            $configPath = "fabric-config.env"
            $envVars | Out-File -FilePath $configPath -Encoding UTF8
            Write-Success "Configuration exported to: $configPath"
        }
        
        # Display summary
        Export-SetupSummary -WorkspaceName $WorkspaceName -WorkspaceId $workspaceId `
            -DatasetName $DatasetName -DatasetId $datasetId -TableName $TableName
        
        Write-Host ""
        Write-Title "NEXT STEPS"
        Write-Host ""
        Write-Host "1. Copy the Workspace ID and Dataset ID values above"
        Write-Host ""
        Write-Host "2. Configure your API environment variables:"
        Write-Host "   - AIHUB_DASHBOARD_METRICS_SOURCE=semantic"
        Write-Host "   - AIHUB_SEMANTIC_METRICS_FILE=/mnt/data/fabric/gold/executive_dashboard_current.json"
        Write-Host ""
        Write-Host "3. For Power BI/Fabric native integration, also configure:"
        Write-Host "   - AIHUB_POWERBI_WORKSPACE_ID=$workspaceId"
        Write-Host "   - AIHUB_POWERBI_DATASET_ID=$datasetId"
        Write-Host "   - AIHUB_POWERBI_TABLE_NAME=$TableName"
        Write-Host ""
        Write-Host "4. Schedule regular data sync using fabric-sync-semantic.ps1:"
        Write-Host "   .\scripts\fabric-sync-semantic.ps1 -WorkspaceId $workspaceId -DatasetId $datasetId"
        Write-Host ""
        Write-Host "5. Verify dashboard data in Power BI/Fabric workspace: $WorkspaceName"
        Write-Host ""
        
    }
    catch {
        Write-Host "`n" -ForegroundColor $ErrorColor
        Write-Host "Setup failed: $_" -ForegroundColor $ErrorColor
        exit 1
    }
}

# Run main
Main
