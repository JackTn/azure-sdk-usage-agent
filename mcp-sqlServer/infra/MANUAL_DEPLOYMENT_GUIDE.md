# Azure Function App (MCP SQL Server) 手动部署指南

## 概述

本文档详细说明了 MCP SQL Server Azure Function App 的所有组件、权限要求和手动部署步骤。

## 📊 架构组件总览

### 当前活跃组件
1. **Azure App Service Plan** (Flex Consumption)
2. **Azure Function App** (Python 3.12)
3. **Azure Storage Account** (用于 Function App 存储)
4. **System-Assigned Managed Identity** (Function App 自动创建)

### 已移除的组件
1. ~~**User-Assigned Managed Identity**~~ (简化架构)
2. ~~**RBAC Role Assignments**~~ (权限问题)
3. ~~**Virtual Network (VNet)**~~ (按要求移除)
4. ~~**Private Endpoints**~~ (按要求移除)
5. ~~**API Management Service**~~ (按要求移除)
6. ~~**Application Insights**~~ (按要求移除)
7. ~~**Log Analytics Workspace**~~ (按要求移除)
8. ~~**MCP 相关配置**~~ (按要求移除)

## 🏗️ 资源创建详情

### 1. Azure App Service Plan
```bash
# 创建 Flex Consumption 计划
az appservice plan create \
  --name "plan-api-<unique-token>" \
  --resource-group "openai-shared" \
  --location "eastus" \
  --sku "FC1" \
  --is-linux true
```

**配置详情**：
- **SKU**: FC1 (Flex Consumption)
- **操作系统**: Linux
- **位置**: East US
- **标签**: `azd-env-name: <environment-name>`

### 2. Azure Storage Account
```bash
# 创建存储账户
az storage account create \
  --name "st<unique-token>" \
  --resource-group "openai-shared" \
  --location "eastus" \
  --sku "Standard_LRS" \
  --kind "StorageV2" \
  --allow-blob-public-access false \
  --allow-shared-key-access false \
  --min-tls-version "TLS1_2" \
  --public-network-access "Enabled"

# 创建部署容器
az storage container create \
  --name "app-package-<function-name>-<hash>" \
  --account-name "st<unique-token>" \
  --auth-mode login
```

**配置详情**：
- **名称模式**: `st{uniqueToken}` (例: stjwthyf3r6tdis)
- **SKU**: Standard_LRS
- **安全配置**:
  - ❌ 禁用公共 Blob 访问
  - ❌ 禁用共享密钥访问 (企业策略要求)
  - ✅ 启用公网访问
  - ✅ 允许 Azure 服务绕过网络 ACL
- **TLS**: 最低 1.2 版本
- **容器**: 自动创建部署包容器

### 3. Azure Function App
```bash
# 创建 Function App
az functionapp create \
  --name "func-api-<unique-token>" \
  --resource-group "openai-shared" \
  --plan "plan-api-<unique-token>" \
  --storage-account "st<unique-token>" \
  --runtime "python" \
  --runtime-version "3.12" \
  --functions-version "4" \
  --os-type "Linux" \
  --assign-identity '[system]'
```

**配置详情**：
- **名称模式**: `func-api-{uniqueToken}`
- **运行时**: Python 3.12
- **Functions 版本**: 4
- **操作系统**: Linux
- **托管标识**: System-Assigned (自动创建)
- **内存**: 2048MB
- **最大实例数**: 100

**应用设置**:
```bash
# 配置应用设置
az functionapp config appsettings set \
  --name "func-api-<unique-token>" \
  --resource-group "openai-shared" \
  --settings \
    "PYTHONPATH=/home/site/wwwroot/.python_packages/lib/site-packages" \
    "AzureWebJobsStorage__credential=managedidentity" \
    "AzureWebJobsStorage__blobServiceUri=https://st<unique-token>.blob.core.windows.net/"
```

## 🔐 权限配置

### 系统分配的托管标识权限

Function App 创建后，会自动生成一个系统分配的托管标识。需要为此标识分配存储权限：

```bash
# 获取 Function App 的系统标识 Principal ID
PRINCIPAL_ID=$(az functionapp identity show \
  --name "func-api-<unique-token>" \
  --resource-group "openai-shared" \
  --query principalId \
  --output tsv)

# 获取存储账户的资源 ID
STORAGE_ID=$(az storage account show \
  --name "st<unique-token>" \
  --resource-group "openai-shared" \
  --query id \
  --output tsv)

# 分配 Storage Blob Data Owner 权限
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "Storage Blob Data Owner" \
  --scope $STORAGE_ID
```

**权限详情**:
- **主体**: Function App 的系统分配托管标识
- **角色**: Storage Blob Data Owner (`b7e6dc6d-f1e8-4753-8033-0f276bb0955b`)
- **作用域**: 存储账户级别
- **用途**: Function App 部署和运行时存储访问

### 用户权限要求

为了执行上述权限分配，操作用户需要：

```bash
# 为用户分配 User Access Administrator 角色
az role assignment create \
  --assignee "v-tianxi@microsoft.com" \
  --role "User Access Administrator" \
  --scope "/subscriptions/faa080af-c1d8-40ad-9cce-e1a450ca5b57/resourceGroups/openai-shared"
```

**权限说明**:
- **角色**: User Access Administrator
- **作用域**: 资源组或订阅级别
- **用途**: 允许为其他主体分配角色权限

## 🚫 已移除组件的原始配置

### User-Assigned Managed Identity (已移除)
```bash
# 原本会创建用户分配的托管标识
az identity create \
  --name "id-api-<unique-token>" \
  --resource-group "openai-shared" \
  --location "eastus"
```

### Virtual Network (已移除)
```bash
# 原本会创建 VNet 和子网
az network vnet create \
  --name "vnet-<unique-token>" \
  --resource-group "openai-shared" \
  --location "eastus" \
  --address-prefixes "10.0.0.0/16"
```

### API Management (已移除)
```bash
# 原本会创建 API Management 服务
az apim create \
  --name "apim-<unique-token>" \
  --resource-group "openai-shared" \
  --location "eastus" \
  --publisher-email "admin@contoso.com" \
  --publisher-name "Administrator"
```

### Application Insights (已移除)
```bash
# 原本会创建 Application Insights
az monitor app-insights component create \
  --app "ai-<unique-token>" \
  --resource-group "openai-shared" \
  --location "eastus" \
  --kind "web"
```

## 📝 部署清单

### ✅ 必须执行的步骤

1. **创建 App Service Plan** (Flex Consumption)
2. **创建 Storage Account** (禁用共享密钥访问)
3. **创建部署容器** (在存储账户中)
4. **创建 Function App** (启用系统标识)
5. **配置应用设置** (托管标识认证)
6. **分配存储权限** (Storage Blob Data Owner)

### ⚠️ 权限前提条件

- 用户必须有 `User Access Administrator` 角色才能分配权限
- 或者让管理员手动分配存储权限给 Function App 的系统标识

### 🔍 验证步骤

1. **检查 Function App 状态**:
   ```bash
   az functionapp show --name "func-api-<unique-token>" --resource-group "openai-shared"
   ```

2. **验证系统标识**:
   ```bash
   az functionapp identity show --name "func-api-<unique-token>" --resource-group "openai-shared"
   ```

3. **检查角色分配**:
   ```bash
   az role assignment list --assignee <principal-id> --scope <storage-account-id>
   ```

4. **测试存储访问**:
   ```bash
   # 在 Function App 控制台中测试
   curl -H "Authorization: Bearer $(az account get-access-token --query accessToken -o tsv)" \
        "https://st<unique-token>.blob.core.windows.net/"
   ```

## 📚 故障排除

### 常见问题

1. **部署存储认证失败**
   - 确认系统标识有 Storage Blob Data Owner 权限
   - 检查存储账户的网络访问控制

2. **企业策略违规**
   - 确认禁用了共享密钥访问
   - 确认使用了托管标识认证

3. **权限分配失败**
   - 确认操作用户有 User Access Administrator 权限
   - 或联系管理员手动分配权限

### 有用的命令

```bash
# 获取唯一令牌 (模拟 Bicep 的 uniqueString)
UNIQUE_TOKEN=$(echo -n "<resource-group-id><environment-name><location>" | sha256sum | cut -c1-13)

# 批量资源名称
APP_PLAN_NAME="plan-api-$UNIQUE_TOKEN"
STORAGE_NAME="st$UNIQUE_TOKEN"
FUNCTION_NAME="func-api-$UNIQUE_TOKEN"
CONTAINER_NAME="app-package-$FUNCTION_NAME-$(echo -n $FUNCTION_NAME$UNIQUE_TOKEN | sha256sum | cut -c1-7)"
```

## 🎯 总结

此手动部署指南创建一个简化但功能完整的 Azure Function App 环境，专注于核心功能而避免了复杂的网络和监控配置。所有组件都配置为使用企业级安全最佳实践，包括托管标识认证和禁用共享密钥访问。
