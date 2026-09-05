targetScope = 'resourceGroup'

@description('Azure region used by the Container Apps.')
param location string = resourceGroup().location

@description('Base application name.')
param appName string = 'aiopportunityhub'

@description('Deployment environment, for example prod.')
param environmentName string = 'prod'

@description('Resource ID of the existing Container Apps Environment.')
param containerAppsEnvironmentId string

@description('Existing Azure Container Registry name.')
param acrName string

@description('Existing Azure Container Registry login server.')
param acrLoginServer string

@description('Existing Storage Account name.')
param storageAccountName string

@description('Existing user-assigned managed identity resource ID.')
param managedIdentityResourceId string

@description('Client ID of the user-assigned managed identity.')
param managedIdentityClientId string

@description('Principal ID of the user-assigned managed identity.')
param managedIdentityPrincipalId string

@description('Immutable API image tag or digest.')
param apiImage string

@description('Immutable frontend image tag or digest.')
param frontendImage string

@description('Versioned Key Vault secret URL containing the PostgreSQL connection URL.')
param databaseSecretUrl string

@description('Existing Key Vault name.')
param keyVaultName string

@description('Exact HTTPS frontend origin allowed by API CORS.')
param allowedOrigins string

@description('Application Insights connection string from the foundation deployment.')
param applicationInsightsConnectionString string

@description('Authentication provider. Keep demo only for non-production validation until Entra support is implemented.')
@allowed([
  'demo'
  'entra'
])
param authProvider string = 'demo'

@description('Tags applied to workloads and role assignments.')
param tags object = {
  application: 'AI Value Hub'
  environment: environmentName
  managedBy: 'Bicep'
}

var apiName = '${appName}-${environmentName}-api'
var frontendName = '${appName}-${environmentName}-frontend'
var acrPullRoleDefinitionId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
var blobContributorRoleDefinitionId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
var keyVaultSecretsUserRoleDefinitionId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6')

resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: acrName
}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: storageAccountName
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

resource acrPullAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(registry.id, managedIdentityPrincipalId, acrPullRoleDefinitionId)
  scope: registry
  properties: {
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: acrPullRoleDefinitionId
  }
}

resource blobContributorAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storage.id, managedIdentityPrincipalId, blobContributorRoleDefinitionId)
  scope: storage
  properties: {
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: blobContributorRoleDefinitionId
  }
}

resource keyVaultSecretsUserAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, managedIdentityPrincipalId, keyVaultSecretsUserRoleDefinitionId)
  scope: keyVault
  properties: {
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: keyVaultSecretsUserRoleDefinitionId
  }
}

resource api 'Microsoft.App/containerApps@2024-03-01' = {
  name: apiName
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityResourceId}': {}
    }
  }
  properties: {
    environmentId: containerAppsEnvironmentId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        allowInsecure: false
        targetPort: 8000
        transport: 'auto'
      }
      registries: [
        {
          server: acrLoginServer
          identity: managedIdentityResourceId
        }
      ]
      secrets: [
        {
          name: 'database-url'
          keyVaultUrl: databaseSecretUrl
          identity: managedIdentityResourceId
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'api'
          image: apiImage
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            {
              name: 'AIHUB_DATABASE_URL'
              secretRef: 'database-url'
            }
            {
              name: 'AIHUB_AUTH_PROVIDER'
              value: authProvider
            }
            {
              name: 'AIHUB_AUTO_SEED_CONTEXT'
              value: 'false'
            }
            {
              name: 'AIHUB_ENABLE_DEMO_SEED'
              value: 'false'
            }
            {
              name: 'AIHUB_ALLOWED_ORIGINS'
              value: allowedOrigins
            }
            {
              name: 'AIHUB_STORAGE_ACCOUNT_NAME'
              value: storageAccountName
            }
            {
              name: 'AIHUB_STORAGE_CONTAINER'
              value: 'documents'
            }
            {
              name: 'AIHUB_REQUIRE_CLOUD_STORAGE'
              value: 'true'
            }
            {
              name: 'AZURE_CLIENT_ID'
              value: managedIdentityClientId
            }
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              value: applicationInsightsConnectionString
            }
          ]
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/health'
                port: 8000
                scheme: 'HTTP'
              }
              initialDelaySeconds: 20
              periodSeconds: 30
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/health'
                port: 8000
                scheme: 'HTTP'
              }
              initialDelaySeconds: 5
              periodSeconds: 10
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
  dependsOn: [
    acrPullAssignment
    blobContributorAssignment
    keyVaultSecretsUserAssignment
  ]
}

resource frontend 'Microsoft.App/containerApps@2024-03-01' = {
  name: frontendName
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityResourceId}': {}
    }
  }
  properties: {
    environmentId: containerAppsEnvironmentId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        allowInsecure: false
        targetPort: 80
        transport: 'auto'
      }
      registries: [
        {
          server: acrLoginServer
          identity: managedIdentityResourceId
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'frontend'
          image: frontendImage
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/'
                port: 80
                scheme: 'HTTP'
              }
              initialDelaySeconds: 10
              periodSeconds: 30
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/'
                port: 80
                scheme: 'HTTP'
              }
              initialDelaySeconds: 5
              periodSeconds: 10
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
  dependsOn: [
    acrPullAssignment
  ]
}

output apiContainerAppName string = api.name
output apiFqdn string = api.properties.configuration.ingress.fqdn
output frontendContainerAppName string = frontend.name
output frontendFqdn string = frontend.properties.configuration.ingress.fqdn
