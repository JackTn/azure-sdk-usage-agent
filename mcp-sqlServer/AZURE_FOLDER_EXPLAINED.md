# .azure 文件夹说明

## 概述

`.azure` 文件夹是由 **Azure Developer CLI (azd)** 自动生成和管理的配置目录，用于存储项目的环境配置和部署状态信息。

## 文件夹结构

```
.azure/
├── config.json          # 全局配置文件
├── .gitignore           # Git 忽略规则
└── dev/                 # 环境目录（以环境名命名）
    ├── .env             # 环境变量文件
    └── config.json      # 环境特定配置
```

## 文件详解

### 1. `.azure/config.json`
**用途**: 存储全局配置信息

```json
{
  "version": 1,
  "defaultEnvironment": "dev"
}
```

- `version`: 配置文件格式版本
- `defaultEnvironment`: 默认使用的环境名称

### 2. `.azure/dev/.env`
**用途**: 存储环境变量和部署后的资源信息

```properties
AZURE_ENV_NAME="dev"
AZURE_FUNCTION_NAME="mcp-mssqlquery"
AZURE_LOCATION="eastus"
AZURE_RESOURCE_GROUP="openai-shared"
AZURE_SUBSCRIPTION_ID="faa080af-c1d8-40ad-9cce-e1a450ca5b57"
SERVICE_API_NAME="mcp-mssqlquery"
```

这些变量包括：
- **AZURE_ENV_NAME**: 环境名称
- **AZURE_FUNCTION_NAME**: 部署的 Function App 名称
- **AZURE_LOCATION**: Azure 区域
- **AZURE_RESOURCE_GROUP**: 资源组名称
- **AZURE_SUBSCRIPTION_ID**: 订阅 ID
- **SERVICE_API_NAME**: API 服务名称

### 3. `.azure/dev/config.json`
**用途**: 存储环境特定的配置参数

```json
{
  "infra": {
    "parameters": {
      "appServicePlanName": "ASP-openaishared-874c"
    }
  }
}
```

## 创建和更新时机

### 创建时机
`.azure` 文件夹在以下情况下被创建：

1. **`azd init`** - 初始化项目时
2. **`azd up`** - 首次部署时
3. **`azd provision`** - 首次预配资源时

### 更新时机
文件夹内容在以下情况下被更新：

1. **`azd up`** - 部署或重新部署时
2. **`azd provision`** - 预配资源时
3. **`azd deploy`** - 仅部署应用代码时
4. **`azd env set`** - 手动设置环境变量时

## 与 Bicep 的关系

| 组件 | 作用 | 关系 |
|------|------|------|
| **Bicep 模板** (`infra/main.bicep`) | 定义要部署的基础设施 | 基础设施即代码 |
| **azd 工具** | 部署编排工具 | 使用 Bicep 模板进行部署 |
| **.azure 文件夹** | 状态和配置管理 | 存储部署状态和环境配置 |

## 工作流程

```mermaid
graph LR
    A[azd init] --> B[创建 .azure 文件夹]
    B --> C[azd up]
    C --> D[读取 Bicep 模板]
    D --> E[部署到 Azure]
    E --> F[更新 .azure 配置]
```

## 版本控制建议

### 应该提交到 Git 的文件：
- `.azure/.gitignore`
- `.azure/config.json` (如果需要共享默认环境)

### 不应该提交到 Git 的文件：
- `.azure/*/` (环境特定目录)
- `.azure/*/.env` (包含敏感信息)
- `.azure/*/config.json` (可能包含环境特定配置)

### .gitignore 示例：
```gitignore
.azure/*
!.azure/.gitignore
!.azure/config.json
```

## 多环境管理

azd 支持多环境部署，每个环境都有自己的目录：

```
.azure/
├── config.json
├── dev/                 # 开发环境
│   ├── .env
│   └── config.json
├── staging/             # 预发布环境
│   ├── .env
│   └── config.json
└── prod/               # 生产环境
    ├── .env
    └── config.json
```

### 环境切换命令：
```bash
# 列出所有环境
azd env list

# 切换到指定环境
azd env select <environment-name>

# 创建新环境
azd env new <environment-name>
```

## 常见问题

### Q: 可以手动编辑 .azure 文件夹中的文件吗？
**A**: 不推荐。这些文件应该由 azd 工具管理。如需修改配置，建议：
- 修改 Bicep 模板参数
- 使用 `azd env set` 命令
- 修改 `infra/main.parameters.json`

### Q: .azure 文件夹丢失了怎么办？
**A**: 可以通过以下方式恢复：
1. 运行 `azd init` 重新初始化
2. 运行 `azd env refresh` 从 Azure 同步状态

### Q: 如何备份 .azure 配置？
**A**: 
1. 备份整个 `.azure` 文件夹
2. 使用 `azd env get-values` 导出环境变量
3. 记录 `azd env list` 的输出

## 总结

`.azure` 文件夹是 Azure Developer CLI 的核心组成部分，它：

- ✅ **自动管理** - 无需手动维护
- ✅ **环境隔离** - 支持多环境配置
- ✅ **状态跟踪** - 记录部署状态和资源信息
- ✅ **配置持久化** - 保存环境变量和参数

理解这个文件夹的作用有助于更好地使用 azd 工具进行 Azure 项目的开发和部署。
