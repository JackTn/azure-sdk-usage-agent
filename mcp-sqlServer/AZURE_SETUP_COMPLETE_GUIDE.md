# Azure Developer CLI 完整环境设置指南

## 文件结构模板

项目包含以下模板文件：
- `.env.template` - 环境变量模板 (必需)
- `.azure-config.template` - 全局配置模板 (可选)
- `.azure-env-config.template` - 环境特定配置模板 (可选)

## .azure 文件夹完整结构

```
.azure/
├── config.json                    # 🌐 全局配置 (默认环境等)
└── dev/                           # 📁 环境目录 (dev/staging/prod)
    ├── .env                       # 🔧 环境变量 (订阅ID、资源名等)
    └── config.json                # ⚙️ 部署参数 (Bicep参数值)
```

## 两个 config.json 的区别

| 文件位置 | 作用范围 | 内容示例 | 用途 |
|----------|----------|----------|------|
| `.azure/config.json` | 🌐 **全局** | `{"defaultEnvironment":"dev"}` | 指定默认环境 |
| `.azure/dev/config.json` | 📁 **单环境** | `{"infra":{"parameters":{...}}}` | 存储部署参数 |

## 首次设置步骤

### 1. 创建目录结构
```bash
mkdir -p .azure/dev
```

### 2. 设置全局配置
```bash
# 方法 1: 使用模板
cp .azure-config.template .azure/config.json

# 方法 2: 直接创建
echo '{"version":1,"defaultEnvironment":"dev"}' > .azure/config.json
```

### 3. 设置环境变量
```bash
# 复制环境变量模板
cp .env.template .azure/dev/.env

# 编辑并填入实际值
vim .azure/dev/.env
```

### 4. 设置环境配置 (可选)
```bash
# 如果需要手动设置部署参数
cp .azure-env-config.template .azure/dev/config.json

# 编辑并填入实际参数值
vim .azure/dev/config.json
```

### 5. 或者使用 azd 命令 (推荐)
```bash
# 创建环境 (自动创建目录和文件)
azd env new dev

# 设置环境变量
azd env set AZURE_SUBSCRIPTION_ID "your-subscription-id"
azd env set AZURE_RESOURCE_GROUP "your-resource-group"
azd env set AZURE_FUNCTION_NAME "your-function-name"
azd env set AZURE_LOCATION "your-location"
```

## 安全提醒

🔒 **绝对不要提交的文件：**
- `.azure/` (整个目录 - 包含敏感信息)
- 任何包含真实订阅 ID 或连接字符串的文件

✅ **安全可以提交的文件：**
- `azure.yaml` - 项目配置 (核心配置文件，必须提交)
- `*.template` 文件 - 环境变量和配置模板
- `infra/*.bicep` - 基础设施代码
- `infra/*.parameters.json` - Bicep 参数模板
- 部署文档和说明

⚠️ **需要评估的文件：**
- `azure.yaml` 中如果包含具体的资源组名称，考虑是否敏感
- 任何包含具体环境信息的配置文件
