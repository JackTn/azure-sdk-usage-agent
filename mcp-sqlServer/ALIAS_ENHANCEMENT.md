# 增强 MCP 工具：添加别名支持

## 为什么需要别名？

在 `getAvailableTablesAndColumns()` 中添加别名信息是非常好的建议，原因如下：

### 🎯 问题场景
用户经常使用各种别名来表达同一个概念：
- **产品名称**：`js` → `JavaScript`、`python` → `Python-SDK`、`c#` → `.Net Code-gen`
- **操作系统**：`mac` → `macOS`、`win` → `Windows`、`ubuntu` → `Linux`
- **HTTP方法**：`get` → `GET`、`create` → `POST`
- **Azure服务**：`vm` → `Microsoft.Compute`、`blob` → `Microsoft.Storage`

### ✅ 解决方案

## 增强的 Schema 返回

现在 `getAvailableTablesAndColumns()` 返回的信息包含：

### 1. 产品别名映射
```json
{
  "name": "Product",
  "product_aliases": {
    "Python-SDK": ["python", "py", "python3"],
    "JavaScript": ["js", "javascript", "node", "nodejs"],
    "Java Fluent": ["java", "jdk"],
    ".Net Code-gen": [".net", "dotnet", "csharp", "c#"]
  },
  "alias_examples": {
    "js_javascript": "js, javascript, node → JavaScript products",
    "python": "python, py → Python-SDK",
    "dotnet": ".net, csharp, c# → .Net products"
  }
}
```

### 2. 常见别名提示
```json
{
  "name": "OS",
  "common_aliases": {
    "windows": "win, windows, microsoft",
    "linux": "linux, ubuntu, debian, centos",
    "macos": "mac, macos, osx, apple"
  }
}
```

### 3. 全局模式映射
```json
{
  "global_aliases": {
    "common_patterns": {
      "time_expressions": {
        "this_month": "2025-08",
        "last_month": "2025-07",
        "recent": "ORDER BY Month DESC"
      },
      "quantity_expressions": {
        "top_n": "SELECT TOP N",
        "most": "ORDER BY [count_column] DESC",
        "total": "SUM([count_column])"
      }
    }
  }
}
```

### 4. AI 提示信息
```json
{
  "ai_hints": {
    "product_matching": "Use product_aliases to map user terms like 'js' to 'JavaScript' products",
    "flexible_filtering": "Use LIKE with % wildcards for partial matches",
    "date_handling": "Month column uses YYYY-MM format, use LIKE for partial matching"
  }
}
```

## 实际效果对比

### 🔥 增强前（硬编码匹配）
```
用户: "显示 js 产品使用情况"
解析器: 可能不理解 "js" 是什么
结果: 查询失败或返回错误结果
```

### ✅ 增强后（智能别名匹配）
```
用户: "显示 js 产品使用情况"
Agent 看到别名信息: js → JavaScript
生成 SQL: SELECT * FROM ProductUsage WHERE Product LIKE '%JavaScript%'
结果: 正确返回 JavaScript 产品数据
```

## 测试示例

运行 `examples/agent_side_processing.py` 可以看到：

### 别名识别测试
- ✅ `js` → 生成 `WHERE Product LIKE '%JavaScript%'`
- ✅ `python` → 生成 `WHERE Product LIKE '%Python%'`  
- ✅ `.net` → 生成 `WHERE Product LIKE '%.Net%'`
- ✅ `c#` → 生成 `WHERE Product LIKE '%.Net%'`
- ✅ `windows` → 生成 `WHERE OS LIKE '%Windows%'`
- ✅ `mac` → 生成 `WHERE OS LIKE '%macOS%'`

### 支持的别名类型

1. **产品别名**：
   - JavaScript: `js`, `javascript`, `node`, `nodejs`
   - Python: `python`, `py`, `python3`
   - .NET: `.net`, `dotnet`, `csharp`, `c#`
   - Java: `java`, `jdk`

2. **操作系统别名**：
   - Windows: `win`, `windows`, `microsoft`
   - Linux: `linux`, `ubuntu`, `debian`, `centos`
   - macOS: `mac`, `macos`, `osx`, `apple`

3. **Azure 服务别名**：
   - Compute: `vm`, `virtual-machine`, `server`
   - Storage: `storage`, `blob`, `file`
   - Network: `vnet`, `subnet`, `nsg`

## 优势

### 🤖 对 AI 的好处
1. **更好的理解**：AI 可以映射用户的各种表达方式
2. **准确匹配**：减少因术语不匹配导致的错误
3. **灵活查询**：支持更自然的用户表达

### 👨‍💻 对用户的好处
1. **自然交互**：可以用习惯的术语
2. **容错性强**：不需要记住精确的产品名称
3. **多语言支持**：支持各种技术栈的常见叫法

### 🔧 对开发者的好处
1. **配置化**：别名信息可以轻松扩展
2. **集中管理**：所有别名在一个地方维护
3. **智能提示**：为 AI 提供足够的上下文

## 扩展建议

可以进一步增强别名系统：

1. **动态别名学习**：从用户查询中学习新的别名模式
2. **多语言支持**：添加中文别名（如：`虚拟机` → `virtualMachines`）
3. **语义相似度**：使用向量相似度匹配相关术语
4. **上下文感知**：根据查询上下文调整别名权重

## 总结

添加别名信息让 MCP 服务对 Agent 端的 AI 更加友好：

- ✅ **提升理解能力**：AI 可以处理各种用户表达方式
- ✅ **保持简单**：MCP 只提供信息，不做复杂处理
- ✅ **易于维护**：别名配置集中且可扩展
- ✅ **增强体验**：用户可以使用自然语言查询

这是一个很好的平衡：**MCP 提供丰富的元数据，Agent 端处理智能逻辑**。
