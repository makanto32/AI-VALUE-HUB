using '../main.bicep'

param workloadName = 'aivaluehub'
param environment = 'dev'
param location = 'eastus2'
param apiImage = 'REPLACE_WITH_REGISTRY/ai-value-hub-api:REPLACE_WITH_VERSION'
param webImage = 'REPLACE_WITH_REGISTRY/ai-value-hub-web:REPLACE_WITH_VERSION'
param entraTenantId = '00000000-0000-0000-0000-000000000000'
param entraClientId = '00000000-0000-0000-0000-000000000000'
param entraAudience = 'api://00000000-0000-0000-0000-000000000000'
param tags = {
  owner: 'REPLACE_WITH_OWNER'
  costCenter: 'REPLACE_WITH_COST_CENTER'
  dataClassification: 'internal'
}
