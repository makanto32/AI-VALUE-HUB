#!/usr/bin/env pwsh

param(
    [Parameter(Mandatory = $true)]
    [string]$SubscriptionId,

    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName,

    [Parameter(Mandatory = $true)]
    [string]$Location,

    [Parameter(Mandatory = $true)]
    [string]$AppName,

    [Parameter(Mandatory = $true)]
    [string]$PostgresAdminLogin,

    [Parameter(Mandatory = $true)]
    [SecureString]$PostgresAdminPassword,

    [string]$EnvironmentName = "prod",
    [string]$ImageTag = "",
    [ValidateSet("demo", "entra")]
    [string]$AuthProvider = "demo"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$foundationTemplate = Join-Path $PSScriptRoot "main.bicep"
$workloadsTemplate = Join-Path $PSScriptRoot "workloads.bicep"
$deploymentName = "aihub-$EnvironmentName-$(Get-Date -Format 'yyyyMMddHHmmss')"

function Assert-Command {
    param([Parameter(Mandatory = $true)][string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' is not installed or is not in PATH."
    }
}

function Assert-LastExitCode {
    param([Parameter(Mandatory = $true)][string]$Operation)
    if ($LASTEXITCODE -ne 0) {
        throw "$Operation failed with exit code $LASTEXITCODE."
    }
}

Assert-Command -Name "az"
Assert-Command -Name "git"

az account set --subscription $SubscriptionId
Assert-LastExitCode -Operation "Azure subscription selection"

$accountId = az account show --query id --output tsv
Assert-LastExitCode -Operation "Azure authentication check"
if ($accountId -ne $SubscriptionId) {
    throw "Azure CLI selected subscription '$accountId', expected '$SubscriptionId'."
}

$gitStatus = git -C $projectRoot status --porcelain
Assert-LastExitCode -Operation "Git status check"
if ($gitStatus) {
    throw "The working tree is dirty. Commit or stash changes before creating production images."
}

if (-not $ImageTag) {
    $ImageTag = git -C $projectRoot rev-parse --short=12 HEAD
    Assert-LastExitCode -Operation "Git image tag calculation"
}
if ($ImageTag -eq "latest" -or $ImageTag -notmatch '^[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}$') {
    throw "Use an immutable valid OCI image tag; 'latest' is not allowed."
}

if ($AuthProvider -eq "demo") {
    Write-Warning "AIHUB_AUTH_PROVIDER=demo is for controlled validation only. Do not onboard production users or client data until Entra token validation is implemented."
}

$plainPassword = [System.Net.NetworkCredential]::new("", $PostgresAdminPassword).Password
try {
    Write-Host "Creating resource group '$ResourceGroupName'..." -ForegroundColor Cyan
    az group create --name $ResourceGroupName --location $Location --output none
    Assert-LastExitCode -Operation "Resource group deployment"

    Write-Host "Deploying private Azure foundation and PostgreSQL..." -ForegroundColor Cyan
    az deployment group create `
        --name $deploymentName `
        --resource-group $ResourceGroupName `
        --template-file $foundationTemplate `
        --parameters `
            location=$Location `
            appName=$AppName `
            environmentName=$EnvironmentName `
            enableAcr=true `
            enablePostgres=true `
            postgresAdminLogin=$PostgresAdminLogin `
            postgresAdminPassword=$plainPassword `
        --output none
    Assert-LastExitCode -Operation "Foundation deployment"

    $outputsJson = az deployment group show `
        --name $deploymentName `
        --resource-group $ResourceGroupName `
        --query properties.outputs `
        --output json
    Assert-LastExitCode -Operation "Foundation output retrieval"
    $outputs = $outputsJson | ConvertFrom-Json

    $acrName = $outputs.acrName.value
    $acrLoginServer = $outputs.acrLoginServer.value
    $environmentId = $outputs.containerAppsEnvironmentId.value
    $defaultDomain = $outputs.containerAppsEnvironmentDefaultDomain.value
    $identityId = $outputs.userAssignedIdentityId.value
    $identityClientId = $outputs.userAssignedIdentityClientId.value
    $identityPrincipalId = $outputs.userAssignedIdentityPrincipalId.value
    $storageAccountName = $outputs.storageAccountName.value
    $keyVaultName = $outputs.keyVaultName.value
    $databaseSecretUrl = $outputs.postgresConnectionSecretUrl.value
    $appInsightsConnectionString = $outputs.applicationInsightsConnectionString.value

    $apiName = "$AppName-$EnvironmentName-api"
    $frontendName = "$AppName-$EnvironmentName-frontend"
    $apiBaseUrl = "https://$apiName.$defaultDomain"
    $frontendOrigin = "https://$frontendName.$defaultDomain"

    Write-Host "Building immutable images in ACR..." -ForegroundColor Cyan
    & (Join-Path $PSScriptRoot "push-to-acr.ps1") `
        -ResourceGroupName $ResourceGroupName `
        -AcrName $acrName `
        -ApiBaseUrl $apiBaseUrl `
        -ImageTag $ImageTag
    if (-not $?) {
        throw "ACR image build failed."
    }

    $apiImage = "$acrLoginServer/ai-value-hub/api`:$ImageTag"
    $frontendImage = "$acrLoginServer/ai-value-hub/frontend`:$ImageTag"

    Write-Host "Deploying API and frontend Container Apps..." -ForegroundColor Cyan
    az deployment group create `
        --name "$deploymentName-workloads" `
        --resource-group $ResourceGroupName `
        --template-file $workloadsTemplate `
        --parameters `
            location=$Location `
            appName=$AppName `
            environmentName=$EnvironmentName `
            containerAppsEnvironmentId=$environmentId `
            acrName=$acrName `
            acrLoginServer=$acrLoginServer `
            storageAccountName=$storageAccountName `
            keyVaultName=$keyVaultName `
            managedIdentityResourceId=$identityId `
            managedIdentityClientId=$identityClientId `
            managedIdentityPrincipalId=$identityPrincipalId `
            apiImage=$apiImage `
            frontendImage=$frontendImage `
            databaseSecretUrl=$databaseSecretUrl `
            allowedOrigins=$frontendOrigin `
            applicationInsightsConnectionString=$appInsightsConnectionString `
            authProvider=$AuthProvider `
        --output none
    Assert-LastExitCode -Operation "Container Apps deployment"

    Write-Host "Deployment completed." -ForegroundColor Green
    Write-Host "Frontend: $frontendOrigin"
    Write-Host "API health: $apiBaseUrl/health"
    Write-Host "API image: $apiImage"
    Write-Host "Frontend image: $frontendImage"
    if ($AuthProvider -eq "demo") {
        Write-Warning "This deployment is infrastructure-complete but not approved for production data while demo authentication is enabled."
    }
}
finally {
    $plainPassword = $null
}
