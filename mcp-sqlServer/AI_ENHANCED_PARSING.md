# AI-Enhanced Query Parsing

## 问题分析

你提到的 `parse_user_query` 方法确实是**硬编码**的实现，存在以下问题：

### 当前硬编码的问题：
1. **规则固化**：大量 if-else 判断和正则表达式
2. **关键词列表固定**：产品别名、资源类型等都是预定义的  
3. **查询模式有限**：只能处理预设的查询模式
4. **扩展性差**：新增查询类型需要修改代码
5. **维护成本高**：需要手动添加新的关键词和规则

## AI 解决方案

我已经为你实现了三种 AI 增强的解析方案：

### 方案1：云端 AI 解析 (`ai_query_parser.py`)
- 使用 OpenAI / Azure OpenAI
- 高准确率，理解能力强
- 需要 API 密钥和网络连接
- 适合生产环境

### 方案2：本地 AI 解析 (`local_ai_query_parser.py`) 
- 使用 Ollama 等本地模型
- 数据不出本地，隐私安全
- 无需 API 费用
- 适合隐私敏感场景

### 方案3：混合模式
- 优先使用本地 AI
- 失败时回退到云端 AI
- 最后回退到规则解析
- 兼顾性能和可靠性

## 使用示例

### 启用本地 AI 解析
```python
from src.main import create_mcp_server

# 使用本地 AI (需要先安装 Ollama)
server = create_mcp_server("local_ai_only")
```

### 启用云端 AI 解析
```python
# 需要先配置 API 密钥
server = create_mcp_server("cloud_ai_only")
```

### 启用混合模式
```python
# 最佳实践：本地优先，云端备用
server = create_mcp_server("hybrid_ai")
```

## 效果对比

### 原始硬编码解析
```python
# 输入："Show me Python SDK usage this month"
# 硬编码规则：
if 'python' in query_lower:
    product_filter = "Product = 'Python-SDK'"
if 'this month' in query_lower:
    date_filter = "Month LIKE '2025-08%'"
```

### AI 增强解析
```python
# 输入："Show me Python SDK usage this month"
# AI 理解：
{
    "table_name": "ProductUsage",
    "columns": ["Month", "Product", "RequestCount"],
    "where_clause": "Product = 'Python-SDK' AND Month LIKE '2025-08%'",
    "reasoning": "用户询问本月Python SDK使用情况"
}
```

## AI 的优势

1. **自然语言理解**：能理解同义词、上下文
2. **灵活性**：无需预定义所有可能的查询模式
3. **自动适应**：能处理新的查询方式
4. **多语言支持**：可以处理中文查询
5. **推理能力**：能根据上下文推断用户意图

## 设置说明

### 本地 AI (Ollama) 设置
```bash
# 1. 安装 Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. 下载模型
ollama pull llama3.1:8b

# 3. 启动服务
ollama serve

# 4. 测试
ollama run llama3.1:8b "Convert: show top 5 products"
```

### 云端 AI 设置
```python
# 在 ai_config.py 中配置
"cloud_ai": {
    "openai_api_key": "your-api-key",
    "model": "gpt-3.5-turbo"
}
```

## 结论

是的，原来的 `parse_user_query` 确实是硬编码的，通过 AI 可以显著改善：

1. **更智能**：理解自然语言而非依赖关键词匹配
2. **更灵活**：处理各种查询表达方式  
3. **更易维护**：无需手动添加规则
4. **更强大**：支持复杂查询和推理

建议从 **本地 AI** 开始尝试，因为：
- 免费使用
- 数据隐私
- 响应快速
- 易于调试

如果本地 AI 效果不理想，再考虑云端 AI 或混合模式。
