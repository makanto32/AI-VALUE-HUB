[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [string] $DisplayName,

    [Parameter(Mandatory)]
    [uri] $WebRedirectUri,

    [string] $TenantId
)

$ErrorActionPreference = 'Stop'
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    throw 'Azure CLI is required.'
}

if ($TenantId) {
    az login --tenant $TenantId --allow-no-subscriptions | Out-Null
}

$existing = az ad app list --display-name $DisplayName --query '[0]' --output json | ConvertFrom-Json
if ($existing) {
    throw "An application named '$DisplayName' already exists. Review it manually to avoid changing an unrelated registration."
}

if ($PSCmdlet.ShouldProcess($DisplayName, 'Create Entra application registration')) {
    $app = az ad app create `
        --display-name $DisplayName `
        --sign-in-audience AzureADMyOrg `
        --web-redirect-uris $WebRedirectUri.AbsoluteUri `
        --enable-id-token-issuance true `
        --output json | ConvertFrom-Json

    $identifierUri = "api://$($app.appId)"
    az ad app update --id $app.id --identifier-uris $identifierUri
    if ($LASTEXITCODE -ne 0) { throw 'Could not configure the Application ID URI.' }

    Write-Host "ENTRA_CLIENT_ID=$($app.appId)"
    Write-Host "ENTRA_AUDIENCE=$identifierUri"
    Write-Host 'Define app roles and grant admin consent using docs/entra-onboarding.md.'
}
