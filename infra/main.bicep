targetScope = 'subscription'

@description('Nombre corto del workload, por ejemplo aivaluehub.')
@minLength(3)
@maxLength(18)
param workloadName string = 'aivaluehub'

@allowed([
  'dev'
  'test'
  'prod'
])
param environment string

@description('Region primaria de Azure.')
param location string = deployment().location

@description('Imagen OCI de la API, incluido el tag inmutable.')
param apiImage string

@description('Imagen OCI del frontend, incluido el tag inmutable.')
param webImage string

@description('Tenant de Entra ID que autenticara a los usuarios.')
param entraTenantId string

@description('Client ID de la App Registration del frontend.')
param entraClientId string

@description('Application ID URI de la API, por ejemplo api://<api-client-id>.')
param entraAudience string

@description('Servidor ACR sin protocolo. Dejar vacio para imagenes publicas.')
param registryServer string = ''

@description('Nombre del ACR. Requerido solo para un ACR privado.')
param registryName string = ''

@description('Grupo de recursos del ACR privado.')
param registryResourceGroupName string = ''

@description('Suscripcion del ACR privado.')
param registrySubscriptionId string = subscription().subscriptionId

param resourceGroupName string = 'rg-${workloadName}-${environment}'
param tags object = {}

var deploymentTags = union(tags, {
  workload: workloadName
  environment: environment
  managedBy: 'bicep'
  solution: 'AI-VALUE-HUB'
})

resource resourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
  tags: deploymentTags
}

module platform 'modules/platform.bicep' = {
  name: 'platform-${environment}'
  scope: resourceGroup
  params: {
    workloadName: workloadName
    environment: environment
    location: location
    apiImage: apiImage
    webImage: webImage
    entraTenantId: entraTenantId
    entraClientId: entraClientId
    entraAudience: entraAudience
    registryServer: registryServer
    registryName: registryName
    registryResourceGroupName: registryResourceGroupName
    registrySubscriptionId: registrySubscriptionId
    tags: deploymentTags
  }
}

output resourceGroupName string = resourceGroup.name
output apiUrl string = platform.outputs.apiUrl
output webUrl string = platform.outputs.webUrl
output keyVaultName string = platform.outputs.keyVaultName
output managedIdentityClientId string = platform.outputs.managedIdentityClientId
