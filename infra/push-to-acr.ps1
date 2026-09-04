#!/usr/bin/env pwsh

param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName,

    [Parameter(Mandatory = $true)]
    [string]$AcrName,

    [Parameter(Mandatory = $true)]
    [string]$ApiBaseUrl,

    [string]$ImageTag = "",
    [string]$RepositoryPrefix = "ai-value-hub"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot

function Assert-Command {
    param([Parameter(Mandatory = $true)][string]$Name)

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' is not installed or is not in PATH."
    }
}

Assert-Command -Name "az"
Assert-Command -Name "git"

$null = az account show --query id -o tsv 2>$null
if ($LASTEXITCODE -ne 0) {
    throw "Azure CLI is not authenticated. Run 'az login' and select the client subscription."
}

$acrLoginServer = az acr show `
    --resource-group $ResourceGroupName `
    --name $AcrName `
    --query loginServer `
    --output tsv
if ($LASTEXITCODE -ne 0 -or -not $acrLoginServer) {
    throw "ACR '$AcrName' was not found in resource group '$ResourceGroupName'."
}

if (-not $ImageTag) {
    $ImageTag = git -C $projectRoot rev-parse --short=12 HEAD
    if ($LASTEXITCODE -ne 0 -or -not $ImageTag) {
        throw "Unable to derive an image tag from the Git commit. Pass -ImageTag explicitly."
    }
}

if ($ImageTag -eq "latest") {
    throw "The mutable tag 'latest' is not allowed. Use a release version or Git commit SHA."
}

if ($ImageTag -notmatch '^[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}$') {
    throw "ImageTag contains characters that are not valid in an OCI tag."
}

$apiRepository = "$RepositoryPrefix/api"
$frontendRepository = "$RepositoryPrefix/frontend"
$apiImage = "$acrLoginServer/$apiRepository`:$ImageTag"
$frontendImage = "$acrLoginServer/$frontendRepository`:$ImageTag"

Write-Host "Building API in Azure Container Registry: $apiImage" -ForegroundColor Cyan
az acr build `
    --registry $AcrName `
    --image "$apiRepository`:$ImageTag" `
    --file "$projectRoot/api/Dockerfile" `
    "$projectRoot/api"
if ($LASTEXITCODE -ne 0) {
    throw "API image build failed."
}

Write-Host "Building frontend in Azure Container Registry: $frontendImage" -ForegroundColor Cyan
az acr build `
    --registry $AcrName `
    --image "$frontendRepository`:$ImageTag" `
    --build-arg "VITE_API_URL=$ApiBaseUrl" `
    --file "$projectRoot/frontend/Dockerfile" `
    "$projectRoot/frontend"
if ($LASTEXITCODE -ne 0) {
    throw "Frontend image build failed."
}

Write-Host "OCI images published successfully." -ForegroundColor Green
Write-Host "API_IMAGE=$apiImage"
Write-Host "FRONTEND_IMAGE=$frontendImage"
Write-Host "IMAGE_TAG=$ImageTag"
