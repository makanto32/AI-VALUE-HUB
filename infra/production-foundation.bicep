targetScope = 'resourceGroup'

@description('Azure region for all AI Value Hub resources.')
param location string = resourceGroup().location

@description('Short base name used to compose globally unique resource names.')
param appName string = 'aivaluehub'

@description('Environment suffix.')
param environmentName string = 'prod'

@description('PostgreSQL administrator login used only to bootstrap the application database.')
param postgresAdminLogin string

@secure()
@description('PostgreSQL administrator password. Store and rotate it under the client secret-management policy.')
param postgresAdminPassword string

@description('Tags applied to the provisioned resources.')
param tags object = {
  application: 'AI Value Hub'
  environment: environmentName
  managedBy: 'Bicep'
}

module foundation 'main.bicep' = {
  name: 'ai-value-hub-production-foundation'
  params: {
    location: location
    appName: appName
    environmentName: environmentName
    tags: tags
    enableAcr: true
    enablePostgres: true
    postgresAdminLogin: postgresAdminLogin
    postgresAdminPassword: postgresAdminPassword
  }
}

output acrName string = foundation.outputs.acrName
output acrLoginServer string = foundation.outputs.acrLoginServer
output containerAppsEnvironmentName string = foundation.outputs.containerAppsEnvironmentName
output keyVaultName string = foundation.outputs.keyVaultName
output managedIdentityId string = foundation.outputs.userAssignedIdentityId
output postgresServerName string = foundation.outputs.postgresServerName
output postgresDatabaseName string = foundation.outputs.postgresDatabaseName
output storageAccountName string = foundation.outputs.storageAccountName