param name string
param location string
param appServicePlanId string
param appSettings object = {}

resource functionApp 'Microsoft.Web/sites@2022-09-01' = {
  name: name
  location: location
  kind: 'functionapp,linux'
  properties: {
    serverFarmId: appServicePlanId
    siteConfig: {
      appSettings: [
        {
          name: 'PYTHONPATH'
          value: '/home/site/wwwroot/.python_packages/lib/site-packages'
        }
        // 其它自定义 appSettings 可在此添加
      ]
    }
  }
}

output SERVICE_API_NAME string = functionApp.name
