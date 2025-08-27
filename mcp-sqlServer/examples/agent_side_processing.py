"""
Agent 端使用 MCP 的示例代码
展示如何在 Agent 端处理自然语言查询
"""
import json
import asyncio
from typing import Dict, Any, Optional

# 模拟 MCP 客户端调用
class MockMCPClient:
    """模拟的 MCP 客户端，实际使用时替换为真实的 MCP 客户端"""
    
    async def call_tool(self, tool_name: str, args: Dict = None) -> Dict[str, Any]:
        """模拟调用 MCP 工具"""
        if tool_name == "getAvailableTablesAndColumns":
            return {
                "success": True,
                "tables": [
                    {
                        "table_name": "ProductUsage",
                        "description": "Product usage statistics by month",
                        "columns": [
                            {
                                "name": "Month", 
                                "type": "string", 
                                "description": "YYYY-MM format"
                            },
                            {
                                "name": "Product", 
                                "type": "string", 
                                "description": "Product name",
                                "enum_values": ["Python-SDK", "JavaScript", "Java Fluent", ".Net Code-gen"],
                                "product_aliases": {
                                    "Python-SDK": ["python", "py", "python3"],
                                    "JavaScript": ["js", "javascript", "node", "nodejs"],
                                    "Java Fluent": ["java", "jdk"],
                                    ".Net Code-gen": [".net", "dotnet", "csharp", "c#"]
                                },
                                "alias_examples": {
                                    "js_javascript": "js, javascript, node → JavaScript products",
                                    "python": "python, py → Python-SDK",
                                    "dotnet": ".net, csharp, c# → .Net products",
                                    "java": "java → Java products"
                                }
                            },
                            {
                                "name": "RequestCount", 
                                "type": "integer", 
                                "description": "Number of requests"
                            },
                            {
                                "name": "SubscriptionCount", 
                                "type": "integer", 
                                "description": "Number of subscriptions"
                            },
                            {
                                "name": "OS",
                                "type": "string",
                                "description": "Operating system",
                                "enum_values": ["Windows", "Linux", "macOS"],
                                "common_aliases": {
                                    "windows": "win, windows, microsoft",
                                    "linux": "linux, ubuntu, debian, centos",
                                    "macos": "mac, macos, osx, apple"
                                }
                            }
                        ],
                        "query_tips": {
                            "date_filtering": "Use LIKE for partial dates: Month LIKE '2024-01%'",
                            "product_matching": "Use aliases for products: 'js' matches JavaScript products",
                            "case_insensitive": "Use LIKE with wildcards for flexible matching",
                            "aggregation": "Use GROUP BY for summaries, ORDER BY for sorting"
                        }
                    }
                ],
                "global_aliases": {
                    "product_aliases": {
                        "js": ["JavaScript"],
                        "python": ["Python-SDK"],
                        "java": ["Java Fluent"],
                        "dotnet": [".Net Code-gen"]
                    },
                    "common_patterns": {
                        "time_expressions": {
                            "this_month": "2025-08",
                            "last_month": "2025-07",
                            "this_year": "2025",
                            "recent": "ORDER BY Month DESC"
                        },
                        "quantity_expressions": {
                            "top_n": "SELECT TOP N",
                            "most": "ORDER BY [count_column] DESC",
                            "least": "ORDER BY [count_column] ASC",
                            "total": "SUM([count_column])"
                        }
                    }
                },
                "ai_hints": {
                    "product_matching": "Use product_aliases to map user terms like 'js' to 'JavaScript' products",
                    "flexible_filtering": "Use LIKE with % wildcards for partial matches",
                    "date_handling": "Month column uses YYYY-MM format, use LIKE for partial matching",
                    "case_sensitivity": "Use LIKE for case-insensitive matching with wildcards"
                }
            }
        elif tool_name == "executeSqlQueryDirect":
            return {
                "success": True,
                "data": [
                    {"Month": "2025-08", "Product": "Python-SDK", "RequestCount": 1500, "SubscriptionCount": 45},
                    {"Month": "2025-08", "Product": "Java Fluent", "RequestCount": 1200, "SubscriptionCount": 38}
                ],
                "row_count": 2
            }
        else:
            return {"error": f"Unknown tool: {tool_name}"}


class SimpleLLMClient:
    """简化的 LLM 客户端，展示如何利用别名信息"""
    
    async def generate_sql(self, prompt: str) -> str:
        """生成 SQL 查询，现在可以更好地处理别名"""
        # 这里是模拟，实际应该调用 OpenAI/Claude/本地模型等
        
        # 从 prompt 中提取用户问题
        user_question = ""
        if "用户问题：" in prompt:
            user_question = prompt.split("用户问题：")[1].split("\n")[0].strip('"')
        
        question_lower = user_question.lower()
        
        # 利用别名信息进行更智能的匹配
        if any(term in question_lower for term in ['js', 'javascript', 'node']):
            return "SELECT TOP 10 Month, Product, RequestCount FROM ProductUsage WHERE Product LIKE '%JavaScript%' ORDER BY RequestCount DESC"
        elif any(term in question_lower for term in ['python', 'py']):
            return "SELECT TOP 10 Month, Product, RequestCount FROM ProductUsage WHERE Product LIKE '%Python%' ORDER BY RequestCount DESC"
        elif any(term in question_lower for term in ['.net', 'dotnet', 'csharp', 'c#']):
            return "SELECT TOP 10 Month, Product, RequestCount FROM ProductUsage WHERE Product LIKE '%.Net%' ORDER BY RequestCount DESC"
        elif any(term in question_lower for term in ['java', 'jdk']):
            return "SELECT TOP 10 Month, Product, RequestCount FROM ProductUsage WHERE Product LIKE '%Java%' ORDER BY RequestCount DESC"
        elif any(term in question_lower for term in ['win', 'windows', 'microsoft']):
            return "SELECT Product, RequestCount, SubscriptionCount FROM ProductUsage WHERE OS LIKE '%Windows%' ORDER BY RequestCount DESC"
        elif any(term in question_lower for term in ['linux', 'ubuntu', 'debian']):
            return "SELECT Product, RequestCount, SubscriptionCount FROM ProductUsage WHERE OS LIKE '%Linux%' ORDER BY RequestCount DESC"
        elif any(term in question_lower for term in ['mac', 'macos', 'osx', 'apple']):
            return "SELECT Product, RequestCount, SubscriptionCount FROM ProductUsage WHERE OS LIKE '%macOS%' ORDER BY RequestCount DESC"
        elif "this month" in question_lower or "本月" in question_lower:
            return "SELECT Product, RequestCount, SubscriptionCount FROM ProductUsage WHERE Month = '2025-08' ORDER BY RequestCount DESC"
        elif "count" in question_lower and "product" in question_lower:
            return "SELECT Product, SUM(RequestCount) as TotalRequests FROM ProductUsage GROUP BY Product ORDER BY TotalRequests DESC"
        else:
            return "SELECT TOP 5 * FROM ProductUsage ORDER BY Month DESC"
    
    async def explain_result(self, query: str, result: Dict, user_question: str) -> str:
        """解释查询结果"""
        if result.get("success"):
            row_count = result.get("row_count", 0)
            return f"根据您的问题「{user_question}」，我执行了查询并找到了 {row_count} 条结果。"
        else:
            return f"查询执行失败：{result.get('error', '未知错误')}"


class SQLAgent:
    """SQL Agent - 处理自然语言查询的主要逻辑"""
    
    def __init__(self, mcp_client, llm_client):
        self.mcp_client = mcp_client
        self.llm_client = llm_client
        self.schema_cache: Optional[Dict] = None
    
    async def initialize(self):
        """初始化 - 获取数据库 schema"""
        print("🔄 正在获取数据库结构...")
        schema_result = await self.mcp_client.call_tool("getAvailableTablesAndColumns")
        
        if schema_result.get("success"):
            self.schema_cache = schema_result
            print("✅ 数据库结构已缓存")
        else:
            raise Exception(f"无法获取数据库结构: {schema_result.get('error')}")
    
    async def process_user_query(self, user_question: str) -> Dict[str, Any]:
        """处理用户查询的主要方法"""
        try:
            # 1. 确保有 schema 信息
            if not self.schema_cache:
                await self.initialize()
            
            print(f"📝 用户问题: {user_question}")
            
            # 2. 构建给 LLM 的 prompt
            prompt = self._build_sql_generation_prompt(user_question)
            
            # 3. 使用 LLM 生成 SQL
            print("🤖 正在生成 SQL 查询...")
            sql_query = await self.llm_client.generate_sql(prompt)
            print(f"🔍 生成的 SQL: {sql_query}")
            
            # 4. 通过 MCP 执行查询
            print("🚀 正在执行查询...")
            result = await self.mcp_client.call_tool(
                "executeSqlQueryDirect", 
                {"sql_query": sql_query}
            )
            
            # 5. 格式化和解释结果
            if result.get("success"):
                explanation = await self.llm_client.explain_result(
                    sql_query, result, user_question
                )
                
                return {
                    "success": True,
                    "user_question": user_question,
                    "generated_sql": sql_query,
                    "data": result["data"],
                    "row_count": result.get("row_count", 0),
                    "explanation": explanation,
                    "processing_method": "Agent-side LLM + MCP execution"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error"),
                    "user_question": user_question,
                    "generated_sql": sql_query
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"处理查询时出错: {str(e)}",
                "user_question": user_question
            }
    
    def _build_sql_generation_prompt(self, user_question: str) -> str:
        """构建给 LLM 的 SQL 生成 prompt，包含详细的别名信息"""
        
        # 提取别名信息
        global_aliases = self.schema_cache.get("global_aliases", {})
        ai_hints = self.schema_cache.get("ai_hints", {})
        
        # 构建表和列信息
        tables_info = []
        for table in self.schema_cache["tables"]:
            columns_desc = []
            for col in table["columns"]:
                col_desc = f"{col['name']} ({col['type']})"
                
                # 添加枚举值
                if col.get("enum_values"):
                    col_desc += f" - values: {', '.join(col['enum_values'][:3])}..."
                
                # 添加别名信息
                if col.get("product_aliases"):
                    aliases_info = []
                    for product, aliases in col["product_aliases"].items():
                        aliases_info.append(f"{product}: {', '.join(aliases[:3])}")
                    col_desc += f" | Aliases: {'; '.join(aliases_info)}"
                
                if col.get("common_aliases"):
                    aliases_info = []
                    for value, aliases in col["common_aliases"].items():
                        aliases_info.append(f"{value}: {aliases}")
                    col_desc += f" | Common aliases: {'; '.join(aliases_info)}"
                
                columns_desc.append(col_desc)
            
            # 添加查询提示
            query_tips = table.get("query_tips", {})
            tips_text = ""
            if query_tips:
                tips_text = f"\nQuery Tips: {'; '.join(query_tips.values())}"
            
            tables_info.append(f"""
Table: {table['table_name']}
Description: {table['description']}
Columns: {', '.join(columns_desc)}{tips_text}
""")
        
        schema_text = '\n'.join(tables_info)
        
        # 构建别名提示
        alias_hints = ""
        if global_aliases.get("product_aliases"):
            alias_hints += f"\nProduct Aliases: {global_aliases['product_aliases']}"
        
        if global_aliases.get("common_patterns"):
            patterns = global_aliases["common_patterns"]
            alias_hints += f"\nTime Patterns: {patterns.get('time_expressions', {})}"
            alias_hints += f"\nQuantity Patterns: {patterns.get('quantity_expressions', {})}"
        
        prompt = f"""
根据以下数据库结构和别名信息生成 SQL 查询：

{schema_text}

别名信息：{alias_hints}

AI 提示：
- {ai_hints.get('product_matching', '')}
- {ai_hints.get('flexible_filtering', '')}
- {ai_hints.get('date_handling', '')}
- {ai_hints.get('case_sensitivity', '')}

用户问题："{user_question}"

要求：
1. 只使用 SELECT 语句
2. 使用 TOP N 来限制结果数量
3. 利用别名信息匹配用户意图（如：js → JavaScript, python → Python-SDK）
4. 使用 LIKE 进行模糊匹配，特别是产品和日期
5. 日期格式通常是 'YYYY-MM'，使用 LIKE 'YYYY-MM%' 进行匹配
6. 对于聚合查询使用 GROUP BY
7. 返回的SQL要能直接执行

请生成合适的 SQL 查询：
"""
        return prompt


# 使用示例
async def main():
    """演示 Agent 端处理流程"""
    
    print("🎯 Agent 端 SQL 查询处理演示")
    print("=" * 50)
    
    # 初始化组件
    mcp_client = MockMCPClient()
    llm_client = SimpleLLMClient()
    agent = SQLAgent(mcp_client, llm_client)
    
    # 测试查询 - 现在包含更多别名测试
    test_questions = [
        "显示本月 Python SDK 的使用情况",
        "js 产品的请求数最多的是哪个？",
        "查看前10个最活跃的 .net 产品",
        "本月 Windows 系统上各产品的订阅数对比",
        "ubuntu 系统上 java 产品的使用情况",
        "node.js 相关产品的总请求数",
        "mac 用户最常用的是什么产品？",
        "c# 开发者的产品使用趋势"
    ]
    
    for question in test_questions:
        print(f"\n📋 测试问题: {question}")
        print("-" * 40)
        
        result = await agent.process_user_query(question)
        
        if result["success"]:
            print(f"✅ 查询成功")
            print(f"🔍 SQL: {result['generated_sql']}")
            print(f"📊 结果数量: {result['row_count']}")
            print(f"💭 解释: {result['explanation']}")
            
            # 显示部分数据
            if result["data"]:
                print("📋 数据示例:")
                for i, row in enumerate(result["data"][:2]):  # 只显示前2行
                    print(f"  {i+1}. {row}")
        else:
            print(f"❌ 查询失败: {result['error']}")
        
        print()


if __name__ == "__main__":
    asyncio.run(main())
