# Azure Functions MCP 服务器部署架构详细分析
# ## 如何改变部署架构？

你可以通过修改以下这些文件来改变 Azure 部署过程和架构：

1. **infra/main.bicep**  
  控制整体资源部署流程和资源组、依赖关系。

2. **infra/app/api.bicep**  
  定义 Function App 的具体配置（运行时、身份、网络等）。

3. **infra/app/rbac.bicep**  
  控制权限分配和角色绑定。

4. **infra/app/vnet.bicep**  
  虚拟网络和子网结构。

5. **infra/app/storage-PrivateEndpoint.bicep**  
  存储账户的私有端点配置。

6. **infra/apim/apim.bicep**  
  API Management 服务相关配置。

7. **infra/app/apim-mcp/mcp-api.bicep**  
  MCP API 的 APIM 集成和策略。

8. **infra/main.parameters.json**  
  部署参数（如环境名、区域、是否启用 VNet）。

9. **azure.yaml**  
  azd 工具的顶层配置，决定用哪个 Bicep 文件和参数。

你可以根据需要修改这些文件，来调整资源类型、数量、配置、网络、安全等部署细节。

## [Reference](https://learn.microsoft.com/zh-cn/azure/azure-resource-manager/bicep/)

## 1. 基础设施即代码 (IaC) 文件

### 主部署模板
- 文件: `infra/main.bicep`
- 内容: 订阅级别部署 (targetScope = 'subscription')，Flex Consumption Function App 配置，托管身份、VNet、APIM 集成，输出变量供应用使用
- 相关文档:
  - [Azure Bicep 文档](https://docs.microsoft.com/azure/azure-resource-manager/bicep/)
  - [Azure Functions Flex Consumption](https://docs.microsoft.com/azure/azure-functions/flex-consumption-plan)

### Function App 配置
- 文件: `infra/app/api.bicep`
- 内容: Flex Consumption Function App，Python 3.12 运行时，托管身份认证，自定义处理程序支持
- 相关文档:
  - [Azure Function App Configuration](https://docs.microsoft.com/azure/azure-functions/functions-app-settings)
  - [Managed Identity for Functions](https://docs.microsoft.com/azure/azure-functions/functions-identity)

### RBAC 权限配置
- 文件: `infra/app/rbac.bicep`
- 内容: Storage Blob Data Owner、Storage Queue Data Contributor、Monitoring Metrics Publisher 等角色分配
- 相关文档:
  - [Azure Built-in Roles](https://docs.microsoft.com/azure/role-based-access-control/built-in-roles)
  - [Role Assignments with Bicep](https://docs.microsoft.com/azure/azure-resource-manager/bicep/bicep-functions-resource)

### 网络和安全配置
- 文件: `infra/app/vnet.bicep`
- 内容: VNet 配置，私有端点子网，应用子网
- 文件: `infra/app/storage-PrivateEndpoint.bicep`
- 内容: 存储账户的私有端点配置，支持 blob/queue/table
- 相关文档:
  - [Virtual Network Integration](https://docs.microsoft.com/azure/azure-functions/functions-networking-options)
  - [Private Endpoints](https://docs.microsoft.com/azure/private-link/private-endpoint-overview)

## 2. Azure Developer CLI 配置

### 主配置文件
- 文件: `azure.yaml`
- 内容: azd 配置，infra 路径，服务类型为 function
- 相关文档:
  - [Azure Developer CLI](https://docs.microsoft.com/azure/developer/azure-developer-cli/)
  - [azd template configuration](https://docs.microsoft.com/azure/developer/azure-developer-cli/azd-schema)

### 参数配置
- 文件: `infra/main.parameters.json`
- 环境变量映射: `${AZURE_ENV_NAME}`、`${AZURE_LOCATION}`、`${AZURE_PRINCIPAL_ID}`、`${VNET_ENABLED}`

## 3. Azure Functions 运行时配置

### 主机配置
- 文件: `host.json`
- 内容: Custom Handler 配置，指向 `mssql_query_server.py`
- 相关文档:
  - [Azure Functions Custom Handlers](https://docs.microsoft.com/azure/azure-functions/functions-custom-handlers)
  - [host.json reference](https://docs.microsoft.com/azure/azure-functions/functions-host-json)

### 函数绑定配置
- 文件: `mcp-handler/function.json`
- 内容: HTTP Trigger 绑定，支持多种 HTTP 方法
- 相关文档:
  - [HTTP Trigger Binding](https://docs.microsoft.com/azure/azure-functions/functions-bindings-http-webhook)
  - [Route Templates](https://docs.microsoft.com/azure/azure-functions/functions-bindings-http-webhook-trigger#route)

## 4. 应用程序代码

### 主入口文件
- 文件: `mssql_query_server.py`
- 功能: 向后兼容包装器，导入模块化组件

### 核心应用逻辑
- 文件: `src/main_with_ai.py`
- 内容: MCP 服务器配置，工具注册 (SQL 查询执行、AI 查询助手)

### 配置管理
- 文件: `src/config.py`
- 用途: 环境变量和配置管理

### 数据库连接
- 文件: `src/sql_client.py`
- 功能: Azure AD 认证的 SQL Server 连接

## 5. 依赖和运行时

### Python 依赖
- 文件: `requirements.txt`
- 关键依赖: httpx、mcp[cli]、azure-identity、pyodbc、azure-kusto-data

### 本地开发配置
- 文件: `local.settings.json`
- 环境变量: FUNCTIONS_WORKER_RUNTIME、SQL_SERVER、SQL_DATABASE 等

## 6. API Management 集成

### APIM 服务配置
- 文件: `infra/apim/apim.bicep`
- SKU: Basicv2 (可配置)

### MCP API 配置
- 文件: `infra/app/apim-mcp/mcp-api.bicep`
- 功能: Function App 集成、OAuth 认证配置、API 策略管理

### 策略文件
- 文件: `infra/app/apim-mcp/mcp-api.policy.xml`、`infra/app/apim-mcp/mcp-prm.policy.xml`

## 7. 命名约定和资源标签

### 缩写定义
- 文件: `infra/abbreviations.json`
- 示例: webSitesFunctions、apiManagementService、storageStorageAccounts、managedIdentityUserAssignedIdentities

## 8. 部署流程

### 部署命令
```bash
azd init
azd up
azd env set AZURE_LOCATION "East US 2"
azd env set VNET_ENABLED true
```

### 环境变量配置
```bash
export AZURE_ENV_NAME="your-env-name"
export AZURE_LOCATION="eastus2"
export AZURE_PRINCIPAL_ID="your-user-id"
export VNET_ENABLED="true"
```

## 9. 相关文档链接汇总

### Azure 官方文档
- [Azure Functions 文档](https://docs.microsoft.com/azure/azure-functions/)
- [Azure Bicep 文档](https://docs.microsoft.com/azure/azure-resource-manager/bicep/)
- [Azure Developer CLI](https://docs.microsoft.com/azure/developer/azure-developer-cli/)
- [Azure API Management](https://docs.microsoft.com/azure/api-management/)

### 最佳实践指南
- [Functions 安全最佳实践](https://docs.microsoft.com/azure/azure-functions/security-concepts)
- [托管身份最佳实践](https://docs.microsoft.com/azure/active-directory/managed-identities-azure-resources/managed-identities-best-practice-recommendations)
- [网络安全最佳实践](https://docs.microsoft.com/azure/azure-functions/functions-networking-options)

### Azure Verified Modules (AVM)
- [AVM Bicep 模块](https://azure.github.io/Azure-Verified-Modules/)
- [Storage Account 模块](https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/storage/storage-account)
- [Function App 模块](https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/web/site)

---

本文件由 GitHub Copilot 自动生成。
