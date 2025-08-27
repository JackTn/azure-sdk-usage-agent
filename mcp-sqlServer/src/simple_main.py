"""
简化版的 MCP SQL Server - 专注于数据访问，AI 逻辑交给 Agent 端
"""
import sys
from mcp.server.fastmcp import FastMCP
from .config import MCP_PORT, SCHEMA_FILE_PATH
from .schema_loader import SchemaLoader
from .simple_mcp_tools import SimpleMCPTools


def create_simple_mcp_server():
    """创建简化的 MCP 服务器 - 只提供数据访问能力"""
    
    print("🚀 启动简化版 MCP SQL Server")
    print("📋 职责：提供 schema 信息 + 安全执行 SQL")
    print("🤖 AI 逻辑：交给 Agent 端处理")
    
    # 初始化 FastMCP 服务器
    mcp = FastMCP("mssqlQuery", stateless_http=True, port=MCP_PORT)
    
    # 初始化组件
    schema_loader = SchemaLoader(SCHEMA_FILE_PATH)
    mcp_tools = SimpleMCPTools(schema_loader)
    
    # 注册核心工具
    @mcp.tool()
    async def getAvailableTablesAndColumns():
        """
        获取可用的表和列信息，供 Agent 端的 LLM 使用
        
        Returns:
            包含所有表结构、列信息、示例查询的 JSON 对象
        """
        return await mcp_tools.get_available_tables_and_columns()

    @mcp.tool()
    async def executeSqlQueryDirect(sql_query: str):
        """
        直接执行 SQL 查询（由 Agent 端生成的 SQL）
        
        Args:
            sql_query: 完整的 SQL SELECT 语句
            
        Returns:
            查询结果的 JSON 对象
        """
        return await mcp_tools.execute_sql_query_direct(sql_query)

    @mcp.tool()
    async def getSampleData(table_name: str, limit: int = 5):
        """
        获取表的示例数据，帮助 Agent 理解数据结构
        
        Args:
            table_name: 表名
            limit: 返回的行数限制
            
        Returns:
            示例数据的 JSON 对象
        """
        return await mcp_tools.get_sample_data(table_name, limit)

    @mcp.tool()
    async def validateAzureAuth():
        """
        验证 Azure AD 认证状态
        
        Returns:
            认证状态的 JSON 对象
        """
        return await mcp_tools.validate_azure_auth()

    # 可选：提供查询建议（Agent 可选择使用）
    @mcp.tool()
    async def suggestQueryStructure(user_intent: str):
        """
        可选工具：基于用户意图提供查询建议
        Agent 可以选择使用、修改或完全忽略这个建议
        
        Args:
            user_intent: 用户的查询意图描述
            
        Returns:
            建议的查询结构 JSON 对象
        """
        return await mcp_tools.suggest_query_structure(user_intent)

    print("✅ MCP 工具注册完成")
    print(f"🌐 服务端口: {MCP_PORT}")
    print("📊 可用工具:")
    print("  - getAvailableTablesAndColumns: 获取数据库结构")
    print("  - executeSqlQueryDirect: 执行 SQL 查询")
    print("  - getSampleData: 获取示例数据")
    print("  - validateAzureAuth: 验证认证")
    print("  - suggestQueryStructure: 查询建议（可选）")
    
    return mcp


def main():
    """主函数"""
    try:
        server = create_simple_mcp_server()
        print("\n🎯 简化版 MCP 服务器已准备就绪")
        print("💡 Agent 端可以使用自己的 LLM 来:")
        print("   1. 理解用户自然语言")
        print("   2. 生成合适的 SQL 查询")
        print("   3. 调用 MCP 执行查询")
        print("   4. 解释和格式化结果")
        server.run()
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
