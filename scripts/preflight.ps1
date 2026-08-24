[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string] $ParametersFile,

    [string] $SubscriptionId
)

$ErrorActionPreference = 'Stop'

function Assert-Command {
    param([string] $Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' was not found."
    }
}

Assert-Command az

$account = az account show --output json 2>$null | ConvertFrom-Json
if (-not $account) {
    throw 'Azure CLI is not authenticated. Run az login first.'
}

if ($SubscriptionId) {
    az account set --subscription $SubscriptionId
    if ($LASTEXITCODE -ne 0) { throw "Cannot select subscription $SubscriptionId." }
    $account = az account show --output json | ConvertFrom-Json
}

$resolvedParameters = (Resolve-Path $ParametersFile).Path
if ($resolvedParameters -notmatch '\.bicepparam$') {
    throw 'ParametersFile must be a .bicepparam file.'
}

$requiredProviders = @(
    'Microsoft.App',
    'Microsoft.ContainerRegistry',
    'Microsoft.Insights',
    'Microsoft.KeyVault',
    'Microsoft.ManagedIdentity',
    'Microsoft.OperationalInsights',
    'Microsoft.Storage'
)

$unregistered = foreach ($provider in $requiredProviders) {
    $state = az provider show --namespace $provider --query registrationState --output tsv
    if ($state -ne 'Registered') { $provider }
}

if ($unregistered) {
    throw "Register these resource providers before deployment: $($unregistered -join ', ')"
}

$mainTemplate = Join-Path $PSScriptRoot '..\infra\main.bicep'
az bicep build --file $mainTemplate --stdout | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Bicep validation failed.' }

Write-Host "Preflight passed for subscription $($account.name) ($($account.id))."
Write-Host "Parameters: $resolvedParameters"
