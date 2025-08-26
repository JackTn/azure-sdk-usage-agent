import json
import azure.functions as func
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from mcp.server.fastmcp import FastMCP
import asyncio

# 公共示例集群，不需要认证
CLUSTER = "https://help.kusto.windows.net"
DATABASE = "Samples"

kcsb = KustoConnectionStringBuilder.with_az_cli_authentication(CLUSTER)
client = KustoClient(kcsb)

# 初始化 MCP
mcp = FastMCP("kusto-mcp")

@mcp.tool()
async def run_kusto_query(query: str) -> str:
    """
    Run a Kusto query against the StormEvents sample table.
    Args:
        query (str): The KQL query string.
    Returns:
        JSON string of query results.
    """
    try:
        response = client.execute(DATABASE, query)
        rows = []
        for row in response.primary_results[0]:
            rows.append(dict(row))
        return json.dumps(rows, indent=2)
    except Exception as e:
        return f"Error running query: {e}"

# Azure Function HTTP Trigger
async def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # 获取请求中的查询语句
        data = req.get_json()
        query = data.get("query")
        if not query:
            return func.HttpResponse("Missing query", status_code=400)

        # 获取新的事件循环并执行查询
        loop = asyncio.get_event_loop()
        result = await run_kusto_query(query)
        return func.HttpResponse(result, mimetype="application/json", status_code=200)

    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
