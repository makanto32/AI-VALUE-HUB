[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string] $ResourceGroupName
)

$ErrorActionPreference = 'Stop'
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    throw 'Azure CLI is required.'
}

$apps = az containerapp list --resource-group $ResourceGroupName --output json | ConvertFrom-Json
if (($apps | Measure-Object).Count -lt 2) {
    throw "Expected API and web Container Apps in $ResourceGroupName."
}

$failures = @()
foreach ($app in $apps) {
    $fqdn = $app.properties.configuration.ingress.fqdn
    if (-not $fqdn) {
        $failures += "$($app.name): missing ingress FQDN"
        continue
    }

    try {
        $response = Invoke-WebRequest -Uri "https://$fqdn" -Method Head -TimeoutSec 30
        Write-Host "$($app.name): HTTP $($response.StatusCode)"
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode -and $statusCode -lt 500) {
            Write-Host "$($app.name): reachable (HTTP $statusCode)"
        }
        else {
            $failures += "$($app.name): $($_.Exception.Message)"
        }
    }
}

$provisioningFailures = az resource list --resource-group $ResourceGroupName `
    --query "[?properties.provisioningState!='Succeeded'].{name:name,state:properties.provisioningState}" `
    --output json | ConvertFrom-Json
if ($provisioningFailures) {
    $failures += "Resources not in Succeeded state: $($provisioningFailures | ConvertTo-Json -Compress)"
}

if ($failures) { throw ($failures -join [Environment]::NewLine) }
Write-Host "Deployment validation passed for $ResourceGroupName."
