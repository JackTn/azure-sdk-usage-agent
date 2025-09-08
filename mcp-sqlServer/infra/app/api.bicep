param name string
@description('Primary location for all resources & Flex Consumption Function App')
param location string = resourceGroup().location
param tags object = {}
param appServicePlanId string
param appSettings object = {}
param runtimeName string 
param runtimeVersion string 
param serviceName string = 'api'
param storageAccountName string
param deploymentStorageContainerName string
param instanceMemoryMB int = 2048
param maximumInstanceCount int = 100

@allowed(['SystemAssigned', 'UserAssigned'])
param identityType string = 'SystemAssigned'  // Default to system assigned

var kind = 'functionapp,linux'

// Create base application settings - Using system assigned managed identity
var baseAppSettings = {
  // Use system assigned managed identity - simpler configuration
  AzureWebJobsStorage__credential: 'managedidentity'
  AzureWebJobsStorage__blobServiceUri: stg.properties.primaryEndpoints.blob
}

// Merge all app settings
var allAppSettings = union(
  appSettings,
  baseAppSettings
)

resource stg 'Microsoft.Storage/storageAccounts@2022-09-01' existing = {
  name: storageAccountName
}

// Create a Flex Consumption Function App to host the API
module api 'br/public:avm/res/web/site:0.15.1' = {
  name: '${serviceName}-flex-consumption'
  params: {
    kind: kind
    name: name
    location: location
    tags: union(tags, { 'azd-service-name': serviceName})
    serverFarmResourceId: appServicePlanId
    managedIdentities: {
      systemAssigned: true  // Use system assigned identity - Azure manages permissions automatically
      userAssignedResourceIds: []  // Remove user assigned identity for now
    }
    functionAppConfig: {
      deployment: {
        storage: {
          type: 'blobContainer'
          value: '${stg.properties.primaryEndpoints.blob}${deploymentStorageContainerName}'
          authentication: {
            type: 'SystemAssignedIdentity'
          }
        }
      }
      scaleAndConcurrency: {
        instanceMemoryMB: instanceMemoryMB
        maximumInstanceCount: maximumInstanceCount
      }
      runtime: {
        name: runtimeName
        version: runtimeVersion
      }
    }
    siteConfig: {
      alwaysOn: false
    }
    appSettingsKeyValuePairs: allAppSettings
  }
}

output SERVICE_API_NAME string = api.outputs.name
// Ensure output is always string, handle potential null from module output if SystemAssigned is not used
output SERVICE_API_IDENTITY_PRINCIPAL_ID string = identityType == 'SystemAssigned' ? api.outputs.?systemAssignedMIPrincipalId ?? '' : ''
