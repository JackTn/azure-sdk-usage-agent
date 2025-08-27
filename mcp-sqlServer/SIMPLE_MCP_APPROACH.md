# Agent 端使用 MCP 的简化方案

## 核心思路

**MCP 服务职责**：
- 提供数据库 schema 信息
- 安全执行 SQL 查询  
- 返回结构化数据

**Agent 端职责**：
- 理解用户自然语言
- 生成合适的 SQL 查询
- 调用 MCP 执行查询
- 格式化和解释结果

## Agent 端实现示例

```python
# Agent 端的查询处理逻辑
class SQLAgent:
    def __init__(self, mcp_client):
        self.mcp_client = mcp_client
        self.schema_cache = None
    
    async def process_user_query(self, user_question: str):
        """处理用户查询 - 在 Agent 端使用 LLM"""
        
        # 1. 获取数据库 schema（如果还没有缓存）
        if not self.schema_cache:
            schema_result = await self.mcp_client.call_tool(
                "getAvailableTablesAndColumns"
            )
            self.schema_cache = schema_result
        
        # 2. 使用 Agent 自己的 LLM 生成 SQL
        sql_query = await self.generate_sql_with_llm(
            user_question, 
            self.schema_cache
        )
        
        # 3. 通过 MCP 执行查询
        result = await self.mcp_client.call_tool(
            "executeSqlQueryDirect", 
            {"sql_query": sql_query}
        )
        
        # 4. 格式化结果
        return self.format_result(result, user_question)
    
    async def generate_sql_with_llm(self, question: str, schema: dict):
        """使用 Agent 的 LLM 生成 SQL"""
        
        # 构建 prompt
        prompt = f"""
        Based on this database schema:
        {json.dumps(schema['tables'], indent=2)}
        
        Generate a SQL query for: "{question}"
        
        Rules:
        - Only use SELECT statements
        - Use TOP N for limiting results
        - Use LIKE for partial string matches
        - Consider common date formats like 'YYYY-MM'
        
        Return only the SQL query, no explanation.
        """
        
        # 调用 Agent 自己的 LLM（OpenAI、Claude、本地模型等）
        sql_query = await self.llm_client.generate(prompt)
        
        return sql_query.strip()
```

## 简化的 MCP 工具注册

```python
# 简化的 main.py
def create_simple_mcp_server():
    mcp = FastMCP("mssqlQuery", stateless_http=True, port=MCP_PORT)
    
    schema_loader = SchemaLoader(SCHEMA_FILE_PATH)
    mcp_tools = SimpleMCPTools(schema_loader)
    
    @mcp.tool()
    async def getAvailableTablesAndColumns():
        """获取可用的表和列信息，供 Agent 端的 LLM 使用"""
        return await mcp_tools.get_available_tables_and_columns()
    
    @mcp.tool()
    async def executeSqlQueryDirect(sql_query: str):
        """直接执行 SQL 查询（由 Agent 端生成）"""
        return await mcp_tools.execute_sql_query_direct(sql_query)
    
    @mcp.tool()
    async def getSampleData(table_name: str, limit: int = 5):
        """获取表的示例数据"""
        return await mcp_tools.get_sample_data(table_name, limit)
    
    @mcp.tool()
    async def validateAzureAuth():
        """验证 Azure 认证"""
        return await mcp_tools.validate_azure_auth()
    
    return mcp
```

## 方案3：混合方案（可选）

如果你想保留一些 MCP 端的智能，可以提供**可选的**查询建议：

```python
@mcp.tool()
async def suggestQueryStructure(user_intent: str):
    """
    可选工具：基于用户意图提供查询建议
    Agent 可以选择使用或忽略这个建议
    """
    return await mcp_tools.suggest_query_structure(user_intent)
```

## Agent 端的完整流程

```python
async def handle_user_question(question: str):
    # 选项1：完全依赖 Agent 的 LLM
    schema = await mcp.getAvailableTablesAndColumns()
    sql = await agent_llm.generate_sql(question, schema)
    result = await mcp.executeSqlQueryDirect(sql)
    
    # 选项2：使用 MCP 的建议（可选）
    suggestion = await mcp.suggestQueryStructure(question)
    # Agent 可以修改建议的 SQL 或完全忽略
    final_sql = await agent_llm.refine_sql(suggestion['suggested_sql'], question)
    result = await mcp.executeSqlQueryDirect(final_sql)
    
    return result
```

## 优势对比

### 简化方案的优势：
1. **MCP 专注本职**：只做数据访问，不做 AI 推理
2. **Agent 端灵活**：可以用任何 LLM，随时升级
3. **部署简单**：MCP 无需 AI 依赖
4. **成本控制**：Agent 端可以选择最优的 LLM
5. **扩展性好**：Agent 可以结合多个 MCP 服务

### 何时需要 MCP 端 AI：
- MCP 服务独立使用（不通过 Agent）
- 需要专业领域的查询解析
- Agent 端没有足够强的 LLM

## 推荐方案

对于你的场景，我推荐**方案1（Agent 端处理）**：

1. 保持 MCP 简单专注
2. 在 Agent 端配置 AI 能力
3. 更灵活，更易维护
4. 符合 MCP 的设计理念

要我帮你实现简化版本吗？
