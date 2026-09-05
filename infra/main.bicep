targetScope = 'resourceGroup'

@description('Primary Azure region for AI Value Hub resources.')
param location string = resourceGroup().location

@description('Base name used to compose Azure resource names.')
param appName string = 'aiopportunityhub'

@description('Deployment environment suffix such as dev, test or prod.')
param environmentName string = 'dev'

@description('Optional tags to stamp across provisioned resources.')
param tags object = {
  application: 'AI Value Hub'
  environment: environmentName
  managedBy: 'Bicep'
}

@description('Enable PostgreSQL Flexible Server provisioning.')
param enablePostgres bool = false

@description('Enable Azure Container Registry provisioning.')
param enableAcr bool = false

@description('Administrator login for PostgreSQL when enabled.')
param postgresAdminLogin string = 'aihubadmin'

@secure()
@description('Administrator password for PostgreSQL when enabled.')
param postgresAdminPassword string = ''

@description('Database created for the AI Value Hub application.')
param postgresDatabaseName string = 'aihub'

@description('Address space used by the production virtual network.')
param virtualNetworkAddressPrefix string = '10.42.0.0/16'

@description('Subnet delegated to the Container Apps Environment. A /23 is recommended for Consumption workloads.')
param containerAppsSubnetPrefix string = '10.42.0.0/23'

@description('Subnet delegated to PostgreSQL Flexible Server.')
param postgresSubnetPrefix string = '10.42.2.0/28'

var effectivePostgresPassword = enablePostgres ? postgresAdminPassword : 'DisabledPostgres123!'

var normalizedApp = toLower(replace(appName, '-', ''))
var shortApp = take(normalizedApp, 14)
var storageName = take('${shortApp}${environmentName}${uniqueString(resourceGroup().id)}', 24)
var acrName = take(replace('${shortApp}${environmentName}acr${uniqueString(resourceGroup().id)}', '-', ''), 50)
var logAnalyticsName = '${appName}-${environmentName}-law'
var appInsightsName = '${appName}-${environmentName}-appi'
var containerAppsEnvName = '${appName}-${environmentName}-cae'
var keyVaultName = take(replace('${appName}-${environmentName}-kv-${uniqueString(resourceGroup().id)}', '-', ''), 24)
var managedIdentityName = '${appName}-${environmentName}-mi'
var postgresServerName = take(replace('${appName}-${environmentName}-psql-${uniqueString(resourceGroup().id)}', '-', ''), 63)
var blobServiceName = 'default'
var virtualNetworkName = '${appName}-${environmentName}-vnet'
var containerAppsSubnetName = 'snet-container-apps'
var postgresSubnetName = 'snet-postgresql'
var postgresPrivateDnsZoneName = 'privatelink.postgres.database.azure.com'

resource virtualNetwork 'Microsoft.Network/virtualNetworks@2024-01-01' = if (enablePostgres) {
  name: virtualNetworkName
  location: location
  tags: tags
  properties: {
    addressSpace: {
      addressPrefixes: [
        virtualNetworkAddressPrefix
      ]
    }
  }
}

resource containerAppsSubnet 'Microsoft.Network/virtualNetworks/subnets@2024-01-01' = if (enablePostgres) {
  parent: virtualNetwork
  name: containerAppsSubnetName
  properties: {
    addressPrefix: containerAppsSubnetPrefix
    delegations: [
      {
        name: 'Microsoft.App.environments'
        properties: {
          serviceName: 'Microsoft.App/environments'
        }
      }
    ]
  }
}

resource postgresSubnet 'Microsoft.Network/virtualNetworks/subnets@2024-01-01' = if (enablePostgres) {
  parent: virtualNetwork
  name: postgresSubnetName
  properties: {
    addressPrefix: postgresSubnetPrefix
    delegations: [
      {
        name: 'Microsoft.DBforPostgreSQL.flexibleServers'
        properties: {
          serviceName: 'Microsoft.DBforPostgreSQL/flexibleServers'
        }
      }
    ]
  }
}

resource postgresPrivateDnsZone 'Microsoft.Network/privateDnsZones@2024-06-01' = if (enablePostgres) {
  name: postgresPrivateDnsZoneName
  location: 'global'
  tags: tags
}

resource postgresPrivateDnsLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = if (enablePostgres) {
  parent: postgresPrivateDnsZone
  name: '${virtualNetworkName}-link'
  location: 'global'
  tags: tags
  properties: {
    registrationEnabled: false
    virtualNetwork: {
      id: virtualNetwork.id
    }
  }
}

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  tags: tags
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: workspace.id
  }
}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  tags: tags
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    supportsHttpsTrafficOnly: true
    accessTier: 'Hot'
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storage
  name: blobServiceName
}

resource documentsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'documents'
  properties: {
    publicAccess: 'None'
  }
}

resource artifactsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'artifacts'
  properties: {
    publicAccess: 'None'
  }
}

resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' = if (enableAcr) {
  #disable-next-line BCP334
  name: acrName
  location: location
  sku: {
    name: 'Standard'
  }
  tags: tags
  properties: {
    adminUserEnabled: false
    publicNetworkAccess: 'Enabled'
    policies: {
      quarantinePolicy: {
        status: 'disabled'
      }
      retentionPolicy: {
        days: 14
        status: 'enabled'
      }
      trustPolicy: {
        status: 'disabled'
        type: 'Notary'
      }
    }
  }
}

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: managedIdentityName
  location: location
  tags: tags
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enabledForDeployment: false
    enabledForTemplateDeployment: false
    enabledForDiskEncryption: false
    publicNetworkAccess: 'Enabled'
    softDeleteRetentionInDays: 90
  }
}

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: containerAppsEnvName
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: workspace.properties.customerId
        sharedKey: workspace.listKeys().primarySharedKey
      }
    }
    workloadProfiles: [
      {
        workloadProfileType: 'Consumption'
        name: 'Consumption'
      }
    ]
    vnetConfiguration: enablePostgres ? {
      infrastructureSubnetId: containerAppsSubnet.id
      internal: false
    } : null
  }
}

resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2023-06-01-preview' = if (enablePostgres) {
  #disable-next-line BCP334
  name: postgresServerName
  location: location
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  tags: tags
  properties: {
    administratorLogin: postgresAdminLogin
    administratorLoginPassword: effectivePostgresPassword
    authConfig: {
      activeDirectoryAuth: 'Disabled'
      passwordAuth: 'Enabled'
      tenantId: subscription().tenantId
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    createMode: 'Default'
    highAvailability: {
      mode: 'Disabled'
    }
    network: {
      delegatedSubnetResourceId: postgresSubnet.id
      privateDnsZoneArmResourceId: postgresPrivateDnsZone.id
      publicNetworkAccess: 'Disabled'
    }
    storage: {
      storageSizeGB: 32
      autoGrow: 'Enabled'
    }
    version: '16'
  }
  dependsOn: [
    postgresPrivateDnsLink
  ]
}

resource postgresDatabase 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-06-01-preview' = if (enablePostgres) {
  parent: postgres
  name: postgresDatabaseName
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

resource postgresConnectionSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = if (enablePostgres) {
  parent: keyVault
  name: 'aihub-database-url'
  properties: {
    value: 'postgresql://${uriComponent(postgresAdminLogin)}:${uriComponent(postgresAdminPassword)}@${postgres!.properties.fullyQualifiedDomainName}:5432/${postgresDatabase!.name}?sslmode=require'
  }
}

output containerAppsEnvironmentId string = containerAppsEnvironment.id
output containerAppsEnvironmentName string = containerAppsEnvironment.name
output containerAppsEnvironmentDefaultDomain string = containerAppsEnvironment.properties.defaultDomain
output acrLoginServer string = enableAcr ? registry!.properties.loginServer : ''
output acrName string = enableAcr ? registry!.name : ''
output acrResourceId string = enableAcr ? registry!.id : ''
output storageAccountName string = storage.name
output storageBlobEndpoint string = storage.properties.primaryEndpoints.blob
output keyVaultName string = keyVault.name
output keyVaultUri string = keyVault.properties.vaultUri
output applicationInsightsConnectionString string = appInsights.properties.ConnectionString
output userAssignedIdentityId string = identity.id
output userAssignedIdentityClientId string = identity.properties.clientId
output userAssignedIdentityPrincipalId string = identity.properties.principalId
output postgresServerName string = enablePostgres ? postgres!.name : ''
output postgresFqdn string = enablePostgres ? postgres!.properties.fullyQualifiedDomainName : ''
output postgresDatabaseName string = enablePostgres ? postgresDatabase!.name : ''
output postgresConnectionSecretUrl string = enablePostgres ? postgresConnectionSecret!.properties.secretUriWithVersion : ''
output documentsContainerName string = documentsContainer.name
output artifactsContainerName string = artifactsContainer.name