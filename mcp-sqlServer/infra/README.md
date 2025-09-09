# Infrastructure (infra) 文件夹说明

## 概述

这个 `infra` 文件夹包含了用于 Azure 基础设施即代码（IaC）部署的 Bicep 模板文件，用于部署一个**简化的** Azure Functions 应用。此版本已移除了 VNet、API Management、Private Endpoints 和 Application Insights 等复杂组件，专注于核心功能。

## 文件结构

### 1. 核心配置文件

| 文件名 | 描述 |
|--------|------|
| `main.bicep` | 简化的主要 Bicep 模板文件，定义了核心基础设施架构 |
| `main.parameters.json` | 参数配置文件，包含环境变量引用 |
| `abbreviations.json` | Azure 资源命名缩写映射表 |
| `bicepconfig.json` | Bicep 配置文件 |

### 2. 模块化子文件夹

#### `app/` - 应用相关的基础设施模块（已简化）
- `api.bicep` - Azure Functions API 配置（移除了 Application Insights 和 VNet 依赖）
- `rbac.bicep` - 角色权限配置（仅包含存储权限）

## 主要参数配置

### 1. 环境参数
- **`environmentName`** - 环境名称（来自 `${AZURE_ENV_NAME}`）
- **`location`** - 部署区域（来自 `${AZURE_LOCATION}`）
- **`principalId`** - 用户身份标识符（来自 `${AZURE_PRINCIPAL_ID}`）

### 2. Azure 服务配置

#### Function App 配置
- **运行时**：Python 3.12
- **SKU**：FlexConsumption (FC1)
- **内存**：2048MB
- **最大实例数**：100
- **网络**：公网访问（简化配置）

#### 存储账户配置
- 禁用公共 Blob 访问
- 禁用共享密钥访问
- 最低 TLS 版本：1.2
- **网络访问**：允许公网访问（简化配置）

### 3. 安全配置
- 用户分配的托管标识
- 基于角色的访问控制 (RBAC) - 仅存储权限
- 禁用本地身份验证方法

## 已移除的组件

为了简化架构，以下组件已被移除：

| 组件类型 | 移除的资源 | 原因 |
|----------|------------|------|
| **网络** | Virtual Network (VNet) | 简化网络配置 |
| **网络** | Private Endpoints | 移除私有网络依赖 |
| **API 管理** | API Management Service | 减少复杂性和成本 |
| **API 管理** | MCP 相关配置 | 移除特定协议配置 |
| **监控** | Application Insights | 移除遥测和监控 |
| **监控** | Log Analytics 工作区 | 移除日志分析功能 |

## 输出参数

| 参数名 | 描述 |
|--------|------|
| `AZURE_LOCATION` | 部署位置 |
| `AZURE_TENANT_ID` | 租户 ID |
| `SERVICE_API_NAME` | API 服务名称 |
| `AZURE_FUNCTION_NAME` | Function App 名称 |

## 架构变化总结

### 简化前 (原始版本)
- 复杂的企业级架构
- 包含 VNet、Private Endpoints、APIM、Application Insights
- 适合生产环境的高安全性要求

### 简化后 (当前版本)
- 基础的 Function App 部署
- 仅包含核心必需组件：Function App + 存储账户 + 托管标识
- 适合开发/测试环境或简单场景

## 部署说明

这个简化版本的基础设施模板提供了：
1. **Azure Function App**（Flex Consumption 计划）
2. **存储账户**（用于 Function App 的依赖）
3. **托管标识**（用于安全访问存储）
4. **RBAC 权限**（存储账户的必要权限）

所有资源都配置为公网访问，简化了网络配置但保持了基本的安全最佳实践。