targetScope = 'resourceGroup'

@description('Primary location for all resources')
@allowed([
  'eastus'
])
param location string

param appServicePlanName string
param apiServiceName string
param storageAccountName string

resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' existing = {
  name: storageAccountName
}

var storageAccountKey = storageAccount.listKeys().keys[0].value

resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' existing = {
  name: appServicePlanName
}

resource functionApp 'Microsoft.Web/sites@2022-09-01' = {
  name: apiServiceName
  location: location
  kind: 'functionapp,linux'
  tags: {
    'azd-service-name': 'api'
  }
  properties: {
    serverFarmId: appServicePlan.id
    reserved: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};AccountKey=${storageAccountKey};EndpointSuffix=${environment().suffixes.storage};'
        }
        {
          name: 'AzureWebJobsStorage__accountName'
          value: storageAccountName
        }
        {
          name: 'AzureWebJobsFeatureFlags'
          value: 'EnableWorkerIndexing'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'custom'
        }
        {
          name: 'FUNCTIONS_CUSTOMHANDLER_PORT'
          value: '8080'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'PYTHONPATH'
          value: '/home/site/wwwroot/.python_packages/lib/site-packages'
        }
        {
          name: 'WEBSITE_RUN_FROM_PACKAGE'
          value: '1'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};AccountKey=${storageAccountKey};EndpointSuffix=${environment().suffixes.storage};'
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: '${toLower(apiServiceName)}-content'
        }
      ]
    }
  }
}

output AZURE_LOCATION string = location
output SERVICE_API_NAME string = functionApp.name
output AZURE_FUNCTION_NAME string = functionApp.name
