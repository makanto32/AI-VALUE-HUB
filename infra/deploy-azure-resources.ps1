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

    [string]$EnvironmentName = "prod"
)

$ErrorActionPreference = "Stop"
$templateFile = Join-Path $PSScriptRoot "production-foundation.bicep"
$deploymentName = "aihub-foundation-$EnvironmentName-$(Get-Date -Format 'yyyyMMddHHmmss')"

if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    throw "Azure CLI is required. Install it and authenticate to the client tenant."
}

az account set --subscription $SubscriptionId
if ($LASTEXITCODE -ne 0) {
    throw "Unable to select Azure subscription '$SubscriptionId'."
}

$selectedSubscription = az account show --query id --output tsv
if ($LASTEXITCODE -ne 0 -or $selectedSubscription -ne $SubscriptionId) {
    throw "Azure CLI is not authenticated to the requested client subscription."
}

$plainPassword = [System.Net.NetworkCredential]::new("", $PostgresAdminPassword).Password
try {
    az group create `
        --name $ResourceGroupName `
        --location $Location `
        --output none
    if ($LASTEXITCODE -ne 0) {
        throw "Resource group creation failed."
    }

    az deployment group create `
        --name $deploymentName `
        --resource-group $ResourceGroupName `
        --template-file $templateFile `
        --parameters `
            location=$Location `
            appName=$AppName `
            environmentName=$EnvironmentName `
            postgresAdminLogin=$PostgresAdminLogin `
            postgresAdminPassword=$plainPassword `
        --output table
    if ($LASTEXITCODE -ne 0) {
        throw "Azure foundation deployment failed."
    }

    Write-Host "Azure production foundation created successfully." -ForegroundColor Green
    Write-Host "Next: build immutable images and deploy the workloads by following docs/ACR_PRODUCTION_DEPLOYMENT.md."
}
finally {
    $plainPassword = $null
}