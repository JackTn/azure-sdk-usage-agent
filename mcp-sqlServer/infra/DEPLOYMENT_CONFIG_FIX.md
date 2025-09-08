# Function App 部署存储配置修复

## 错误分析
```
MissingDeploymentConfigException: functionAppConfig > deployment > storage is missing following configurations: 
AppSetting name set in authentication > value does not exist.
```

## 问题原因
之前的配置尝试使用用户分配的托管标识进行部署存储认证，但是：
1. 在部署时，托管标识可能还没有必要的权限
2. 配置中引用的应用设置可能不存在或不正确

## 解决方案

### 修改内容
1. **启用系统分配的托管标识**用于部署：
   ```bicep
   managedIdentities: {
     systemAssigned: true  // 专门用于部署存储访问
     userAssignedResourceIds: [
       '${identityId}'     // 用于运行时存储访问
     ]
   }
   ```

2. **使用系统分配的标识进行部署存储认证**：
   ```bicep
   deployment: {
     storage: {
       type: 'blobContainer'
       value: '${stg.properties.primaryEndpoints.blob}${deploymentStorageContainerName}'
       authentication: {
         type: 'SystemAssignedIdentity'  // 使用系统分配的标识
       }
     }
   }
   ```

3. **运行时仍使用用户分配的托管标识**：
   ```bicep
   // 应用设置中继续使用用户分配的托管标识
   AzureWebJobsStorage__credential: 'managedidentity'
   AzureWebJobsStorage__clientId: identityClientId
   AzureWebJobsStorage__blobServiceUri: stg.properties.primaryEndpoints.blob
   ```

### 为什么这样修复？

1. **系统分配的托管标识**：
   - Azure 自动为其分配基本的权限
   - 更适合用于部署阶段的存储访问
   - 减少配置复杂性

2. **用户分配的托管标识**：
   - 保持用于运行时的存储访问
   - 更好的权限控制
   - 可以在多个资源间共享

### 预期结果
- ✅ 部署存储配置正确
- ✅ Function App 能够成功部署代码包
- ✅ 运行时能够访问存储进行正常操作
- ✅ 符合企业安全策略（不使用共享密钥）

### 如果仍有问题
如果部署后 Function App 无法访问存储，可能需要：
1. 手动为系统分配的托管标识分配存储 Blob 数据贡献者权限
2. 为用户分配的托管标识分配运行时所需的权限
