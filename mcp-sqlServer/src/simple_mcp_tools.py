"""
简化的 MCP 工具 - 只保留核心功能，AI 解析交给 Agent 端处理
"""
from typing import Any, Dict, List
from .sql_client import MSSQLRestClient
from .schema_loader import SchemaLoader
from .query_parser import QueryParser
from .product_aliases import ProductAliasMapper
from .config import SQL_SERVER, SQL_DATABASE, AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP


class SimpleMCPTools:
    """简化的 MCP 工具 - 专注于数据查询，不处理复杂的 NL 解析"""
    
    def __init__(self, schema_loader: SchemaLoader):
        self.sql_client = MSSQLRestClient()
        self.schema_loader = schema_loader
        self.query_parser = QueryParser(schema_loader)  # 保留基础解析作为备用
        self.product_mapper = ProductAliasMapper()  # 添加产品别名映射器
    
    async def get_available_tables_and_columns(self) -> Dict[str, Any]:
        """
        返回可用的表和列信息，包含别名信息，让 Agent 自己决定如何查询
        这样 Agent 可以用自己的 LLM 来理解用户意图
        """
        try:
            enabled_tables = self.schema_loader.get_enabled_tables()
            tables_info = []
            
            for table_key, table_info in enabled_tables.items():
                column_details = []
                
                for col in table_info.columns:
                    col_detail = {'name': col}
                    if col in table_info.column_metadata:
                        meta = table_info.column_metadata[col]
                        col_detail.update({
                            'type': meta.get('type', 'string'),
                            'description': meta.get('description', ''),
                            'enum_values': meta.get('enum')[:10] if meta.get('enum') else None  # 只返回前10个示例
                        })
                        
                        # 为特定列添加别名信息
                        if col == 'Product' and meta.get('enum'):
                            # 为每个产品添加别名信息
                            product_aliases = {}
                            for product in meta.get('enum', []):
                                aliases = list(self.product_mapper.get_aliases_for_product(product))
                                if aliases:
                                    product_aliases[product] = aliases
                            
                            if product_aliases:
                                col_detail['product_aliases'] = product_aliases
                                col_detail['alias_examples'] = {
                                    'js_javascript': 'js, javascript, node → JavaScript products',
                                    'python': 'python, py → Python-SDK',
                                    'dotnet': '.net, csharp, c# → .Net products',
                                    'java': 'java → Java products',
                                    'go': 'go, golang → Go-SDK'
                                }
                        
                        # 为其他可能有别名的列添加提示
                        elif col == 'OS':
                            col_detail['common_aliases'] = {
                                'windows': 'win, windows, microsoft',
                                'linux': 'linux, ubuntu, debian, centos',
                                'macos': 'mac, macos, osx, apple'
                            }
                        elif col == 'HttpMethod':
                            col_detail['common_aliases'] = {
                                'GET': 'get, read, fetch',
                                'POST': 'post, create, add',
                                'PUT': 'put, update, modify',
                                'DELETE': 'delete, remove'
                            }
                        elif col == 'Provider':
                            col_detail['common_patterns'] = {
                                'compute': 'Microsoft.Compute, VM, virtual machines',
                                'storage': 'Microsoft.Storage, blob, storage accounts',
                                'network': 'Microsoft.Network, VNet, networking',
                                'web': 'Microsoft.Web, app service, websites'
                            }
                        elif col == 'Resource':
                            col_detail['common_patterns'] = {
                                'vm': 'virtualMachines, VM, virtual machines',
                                'storage': 'storageAccounts, blob, storage',
                                'network': 'virtualNetworks, VNet, subnet',
                                'webapp': 'webApps, app service, websites'
                            }
                    
                    column_details.append(col_detail)
                
                # 为表添加查询示例和别名提示
                sample_queries = [
                    f"SELECT TOP 10 * FROM {table_info.name}",
                    f"SELECT Month, COUNT(*) FROM {table_info.name} GROUP BY Month",
                    f"SELECT * FROM {table_info.name} WHERE Month LIKE '2024%'"
                ]
                
                # 如果有 Product 列，添加产品相关的示例
                if 'Product' in table_info.columns:
                    sample_queries.extend([
                        f"SELECT * FROM {table_info.name} WHERE Product LIKE '%Python%'",
                        f"SELECT Product, SUM(RequestCount) FROM {table_info.name} GROUP BY Product"
                    ])
                
                tables_info.append({
                    "table_name": table_info.name,
                    "description": table_info.description,
                    "columns": column_details,
                    "sample_queries": sample_queries,
                    "query_tips": {
                        "date_filtering": "Use LIKE for partial dates: Month LIKE '2024-01%'",
                        "product_matching": "Use aliases for products: 'js' matches JavaScript products",
                        "case_insensitive": "Use LIKE with wildcards for flexible matching",
                        "aggregation": "Use GROUP BY for summaries, ORDER BY for sorting"
                    }
                })
            
            # 添加全局别名信息供 AI 参考
            global_aliases = {
                "product_aliases": self.product_mapper.get_all_aliases(),
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
                    },
                    "comparison_expressions": {
                        "more_than": "> value",
                        "less_than": "< value",
                        "at_least": ">= value",
                        "exactly": "= value"
                    }
                }
            }
            
            return {
                "success": True,
                "tables": tables_info,
                "global_aliases": global_aliases,
                "ai_hints": {
                    "product_matching": "Use product_aliases to map user terms like 'js' to 'JavaScript' products",
                    "flexible_filtering": "Use LIKE with % wildcards for partial matches",
                    "date_handling": "Month column uses YYYY-MM format, use LIKE for partial matching",
                    "case_sensitivity": "Use LIKE for case-insensitive matching with wildcards"
                },
                "note": "Agent can use its own LLM to generate queries based on this enhanced schema with aliases"
            }
        except Exception as e:
            return {"error": f"Error retrieving schema: {str(e)}"}
    
    async def execute_sql_query_direct(self, sql_query: str) -> Dict[str, Any]:
        """
        直接执行 SQL 查询 - 让 Agent 自己生成 SQL
        MCP 只负责安全执行和返回结果
        """
        try:
            # 基本安全检查
            sql_lower = sql_query.lower().strip()
            
            if not sql_lower.startswith('select'):
                return {"error": "Only SELECT queries are allowed"}
            
            # 简单的危险操作检查
            dangerous_keywords = ['drop', 'delete', 'insert', 'update', 'create', 'alter', 'truncate']
            if any(keyword in sql_lower for keyword in dangerous_keywords):
                return {"error": "Query contains prohibited operations"}
            
            # 执行查询
            query_result = await self.sql_client.execute_query_via_rest(sql_query)
            
            # 格式化结果
            result_data = []
            for row in query_result.get("rows", []):
                row_dict = {}
                for i, value in enumerate(row):
                    column_name = query_result.get("columns", [])[i] if i < len(query_result.get("columns", [])) else f"column_{i}"
                    row_dict[column_name] = value
                result_data.append(row_dict)
            
            return {
                "success": True,
                "query": sql_query,
                "data": result_data,
                "row_count": len(result_data),
                "columns": query_result.get("columns", [])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing query: {str(e)}",
                "query": sql_query
            }
    
    async def get_sample_data(self, table_name: str, limit: int = 5) -> Dict[str, Any]:
        """
        获取表的示例数据，帮助 Agent 理解数据结构
        """
        try:
            sql_query = f"SELECT TOP {limit} * FROM {table_name}"
            return await self.execute_sql_query_direct(sql_query)
        except Exception as e:
            return {"error": f"Error getting sample data: {str(e)}"}
    
    async def suggest_query_structure(self, user_intent: str) -> Dict[str, Any]:
        """
        基于用户意图提供查询建议 - 这是可选的，主要用于 Agent 参考
        """
        try:
            # 使用现有的简单解析器提供建议
            parsed = self.query_parser.parse_user_query(user_intent)
            
            if 'error' in parsed:
                return {
                    "suggestions": [
                        "Try asking about specific tables: products, customers, usage",
                        "Include time filters: 'this month', '2024-01'",
                        "Ask for aggregations: 'top 10', 'count by month'",
                        "Filter by specific values: 'Python SDK', 'Windows OS'"
                    ]
                }
            
            # 构建建议的 SQL
            columns_str = ', '.join(parsed['columns']) if parsed['columns'] else '*'
            suggested_sql = f"SELECT {columns_str} FROM {parsed['table_name']}"
            
            if parsed['where_clause'] != '1=1':
                suggested_sql += f" WHERE {parsed['where_clause']}"
            
            if parsed['order_clause']:
                suggested_sql += f" {parsed['order_clause']}"
            
            if parsed['limit_clause']:
                suggested_sql = suggested_sql.replace('SELECT', f"SELECT {parsed['limit_clause']}")
            
            return {
                "suggested_sql": suggested_sql,
                "explanation": "This is a suggestion based on simple parsing. Agent can modify as needed.",
                "components": {
                    "table": parsed['table_name'],
                    "columns": parsed['columns'],
                    "filters": parsed['where_clause'] if parsed['where_clause'] != '1=1' else None,
                    "ordering": parsed['order_clause'] if parsed['order_clause'] else None,
                    "limit": parsed['limit_clause'] if parsed['limit_clause'] else None
                }
            }
            
        except Exception as e:
            return {"error": f"Error suggesting query: {str(e)}"}

    # 保留原有的认证方法
    async def validate_azure_auth(self) -> Dict[str, Any]:
        """验证 Azure AD 认证"""
        try:
            sql_token = await self.sql_client.get_access_token(self.sql_client.sql_scope)
            mgmt_token = await self.sql_client.get_access_token(self.sql_client.management_scope)
            
            return {
                "success": True,
                "message": "Azure AD authentication successful",
                "server": SQL_SERVER,
                "database": SQL_DATABASE
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Azure AD authentication failed: {str(e)}"
            }
