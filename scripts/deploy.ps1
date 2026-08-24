[CmdletBinding(SupportsShouldProcess)]
param(
    [ValidateSet('dev', 'test', 'prod')]
    [string] $Environment = 'dev',

    [string] $Location = 'eastus2',

    [string] $SubscriptionId,

    [string] $ParametersFile,

    [switch] $SkipWhatIf
)

$ErrorActionPreference = 'Stop'
$templateFile = Join-Path $PSScriptRoot '..\infra\main.bicep'
if (-not $ParametersFile) {
    $candidate = Join-Path $PSScriptRoot "..\infra\environments\$Environment.bicepparam"
    if (-not (Test-Path $candidate)) {
        throw "Create $candidate from the provided example before deploying $Environment."
    }
    $ParametersFile = $candidate
}

$preflightArgs = @{ ParametersFile = $ParametersFile }
if ($SubscriptionId) { $preflightArgs.SubscriptionId = $SubscriptionId }
& (Join-Path $PSScriptRoot 'preflight.ps1') @preflightArgs

$deploymentName = "ai-value-hub-$Environment-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
$commonArgs = @(
    '--name', $deploymentName,
    '--location', $Location,
    '--template-file', $templateFile,
    '--parameters', $ParametersFile
)

if (-not $SkipWhatIf) {
    az deployment sub what-if @commonArgs
    if ($LASTEXITCODE -ne 0) { throw 'Azure what-if failed.' }
}

if ($PSCmdlet.ShouldProcess("Azure subscription deployment $deploymentName", 'Deploy')) {
    az deployment sub create @commonArgs --output json
    if ($LASTEXITCODE -ne 0) { throw 'Azure deployment failed.' }
}
