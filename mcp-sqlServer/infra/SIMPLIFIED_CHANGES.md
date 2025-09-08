# 基础设施简化修改总结

## 修改概览

根据你的要求，我已经成功简化了 MCP SQL Server 的 Azure 基础设施模板，移除了以下不需要的组件：

### 移除的组件

1. **Virtual Network (VNet) 相关**
   - `app/vnet.bicep` 模块调用
   - VNet 参数和配置
   - 网络子网集成

2. **API Management 和 MCP 相关配置**
   - `apim/apim.bicep` 模块
   - `app/apim-mcp/` 下的所有 MCP 配置
   - MCP Entra 应用配置
   - API Management 服务部署

3. **Private Endpoints**
   - `app/storage-PrivateEndpoint.bicep` 模块
   - 存储账户私有终结点配置

4. **Azure Application Insights 和 Log Analytics**
   - Application Insights 组件
   - Log Analytics 工作区
   - 相关的监控配置和角色分配

## 保留的核心组件

### 1. Azure Function App
- **计划类型**: Flex Consumption (FC1)
- **运行时**: Python 3.12
- **内存**: 2048MB
- **最大实例数**: 100
- **操作系统**: Linux

### 2. 存储账户
- **网络访问**: 公网访问（简化配置）
- **安全设置**: 
  - 禁用公共 Blob 访问
  - 禁用共享密钥访问
  - 最低 TLS 版本 1.2

### 3. 托管标识和权限
- **用户分配的托管标识**
- **RBAC 权限**:
  - Storage Blob Data Owner（用于 Function App）
  - Storage Queue Data Contributor（可选）
  - Storage Table Data Contributor（可选）

## 文件修改详情

### 1. `main.bicep` - 主模板文件
**主要修改**:
- 移除了所有 VNet 相关参数和变量
- 移除了 API Management 部署
- 移除了 MCP Entra 应用配置
- 移除了 Application Insights 和 Log Analytics 模块
- 移除了 Private Endpoint 模块
- 简化了存储账户配置（公网访问）
- 更新了 API 模块调用参数

### 2. `app/api.bicep` - Function App 模块
**主要修改**:
- 移除了 `applicationInsightsName` 参数
- 移除了 `virtualNetworkSubnetId` 参数
- 移除了 Application Insights 相关的应用设置
- 移除了 Application Insights 资源引用
- 移除了 VNet 子网集成配置

### 3. `app/rbac.bicep` - 权限配置模块
**主要修改**:
- 移除了 `appInsightsName` 参数
- 移除了 Application Insights 相关的角色分配
- 移除了 Application Insights 资源引用
- 保留了存储账户的所有权限配置

### 4. `main.parameters.json` - 参数文件
**主要修改**:
- 移除了 `vnetEnabled` 参数

### 5. `README.md` - 文档更新
- 完全重写了文档，反映简化后的架构
- 添加了"已移除的组件"部分
- 更新了架构变化总结

## 部署验证

所有修改后的文件都已通过 Bicep 语法验证，没有发现错误。

## 输出参数变化

**移除的输出**:
- `APPLICATIONINSIGHTS_CONNECTION_STRING`

**保留的输出**:
- `AZURE_LOCATION`
- `AZURE_TENANT_ID` 
- `SERVICE_API_NAME`
- `AZURE_FUNCTION_NAME`

## 成本和复杂性影响

**成本降低**:
- 移除了 API Management（每月约 $100+）
- 移除了 Application Insights 的数据摄取成本
- 移除了 Log Analytics 的存储成本
- 移除了 Private Endpoint 的费用

**复杂性降低**:
- 网络配置大大简化
- 减少了需要管理的组件数量
- 减少了权限配置的复杂性
- 简化了故障排除过程

这个简化版本非常适合开发/测试环境或者不需要企业级安全和监控功能的简单部署场景。
