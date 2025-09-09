# 存储账户策略问题解决方案

## 问题描述
组织策略禁止存储账户使用共享密钥访问（Local authentication methods），导致部署失败。

## 解决方案
改为使用托管标识认证，但不预先创建 RBAC 角色分配，依赖 Azure 的内置权限机制。

## 修改内容

### 1. 存储账户配置
```bicep
// 禁用共享密钥访问以符合策略
allowSharedKeyAccess: false 
```

### 2. Function App 认证配置
```bicep
// 使用托管标识和明确的端点配置
AzureWebJobsStorage__credential: 'managedidentity'
AzureWebJobsStorage__clientId: identityClientId
AzureWebJobsStorage__blobServiceUri: stg.properties.primaryEndpoints.blob
```

## 关键点

### ✅ 优势
1. **符合企业安全策略** - 不使用共享密钥
2. **使用最佳实践** - 托管标识认证
3. **避免权限问题** - 不需要创建 RBAC 角色分配

### ⚠️ 注意事项
1. **可能的权限延迟** - 托管标识权限可能需要几分钟才能生效
2. **依赖内置权限** - 依赖 Azure 的默认权限机制
3. **部署后验证** - 需要验证 Function App 能否正常访问存储

### 🔍 故障排除
如果 Function App 仍然无法访问存储：

1. **等待权限生效**（通常 5-10 分钟）
2. **手动分配权限**：
   ```bash
   # 为托管标识分配存储 Blob 数据所有者角色
   az role assignment create \
     --assignee <managed-identity-client-id> \
     --role "Storage Blob Data Owner" \
     --scope "/subscriptions/<subscription-id>/resourceGroups/<rg-name>/providers/Microsoft.Storage/storageAccounts/<storage-name>"
   ```

3. **检查存储账户防火墙设置**

## 预期结果
- ✅ 通过策略验证
- ✅ 使用安全的托管标识认证
- ✅ Function App 能够访问存储进行代码部署和运行时操作
