"""
AI-powered query parser using language models for natural language to SQL conversion
"""
import json
import re
from typing import Any, Dict, List, Optional
from .models import QueryInfo
from .schema_loader import SchemaLoader

# You can use OpenAI, Azure OpenAI, or any other LLM service
# Example using OpenAI (you'll need to install openai package)
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class AIQueryParser:
    """AI-powered query parser using language models"""
    
    def __init__(self, schema_loader: SchemaLoader, ai_config: Optional[Dict] = None):
        self.schema_loader = schema_loader
        self.ai_config = ai_config or {}
        
        if HAS_OPENAI and self.ai_config.get('openai_api_key'):
            openai.api_key = self.ai_config['openai_api_key']
            self.use_ai = True
        else:
            self.use_ai = False
            print("Warning: OpenAI not available, falling back to rule-based parsing")
    
    def get_schema_context(self) -> str:
        """Generate schema context for AI model"""
        enabled_tables = self.schema_loader.get_enabled_tables()
        schema_info = []
        
        for table_key, table_info in enabled_tables.items():
            table_desc = f"Table: {table_info.name}\n"
            table_desc += f"Description: {table_info.description}\n"
            table_desc += f"Columns: {', '.join(table_info.columns)}\n"
            
            # Add column metadata
            for col in table_info.columns:
                if col in table_info.column_metadata:
                    meta = table_info.column_metadata[col]
                    table_desc += f"  - {col}: {meta.get('description', '')}"
                    if meta.get('enum'):
                        table_desc += f" (enum: {', '.join(meta['enum'][:5])}{'...' if len(meta['enum']) > 5 else ''})"
                    table_desc += "\n"
            
            schema_info.append(table_desc)
        
        return "\n\n".join(schema_info)
    
    def create_prompt(self, user_question: str) -> str:
        """Create prompt for AI model"""
        schema_context = self.get_schema_context()
        
        prompt = f"""
You are a SQL query generator. Given a natural language question and database schema, 
generate the appropriate SQL query components.

Database Schema:
{schema_context}

User Question: "{user_question}"

Please analyze the question and provide a JSON response with the following structure:
{{
    "table_name": "most appropriate table name",
    "columns": ["list", "of", "relevant", "columns"],
    "where_clause": "SQL WHERE conditions (without WHERE keyword)",
    "order_clause": "SQL ORDER BY clause (with ORDER BY keyword)",
    "limit_clause": "SQL TOP N clause (with TOP keyword)",
    "confidence": 0.95,
    "reasoning": "explanation of choices made"
}}

Rules:
1. If asking for "top N" items, use "TOP N" in limit_clause
2. For date filtering, use LIKE for partial matches (e.g., "Month LIKE '2024-01%'")
3. For product filtering, match against enum values
4. Always include key columns like Month, RequestCount, SubscriptionCount when relevant
5. Use confidence score 0-1 based on how certain you are about the interpretation
6. If unclear, return confidence < 0.7 and explain in reasoning

Return only valid JSON, no other text.
"""
        return prompt
    
    async def parse_with_ai(self, user_question: str) -> Dict[str, Any]:
        """Parse user question using AI model"""
        if not self.use_ai:
            return {"error": "AI parsing not available"}
        
        try:
            prompt = self.create_prompt(user_question)
            
            # Use OpenAI API (you can replace with Azure OpenAI or other providers)
            response = await openai.ChatCompletion.acreate(
                model=self.ai_config.get('model', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "system", "content": "You are a SQL expert that converts natural language to SQL components."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                result = json.loads(ai_response)
                
                # Validate required fields
                required_fields = ['table_name', 'columns', 'where_clause']
                for field in required_fields:
                    if field not in result:
                        return {"error": f"AI response missing required field: {field}"}
                
                # Validate table exists
                enabled_tables = self.schema_loader.get_enabled_tables()
                table_found = False
                for table_key, table_info in enabled_tables.items():
                    if table_info.name == result['table_name']:
                        table_found = True
                        break
                
                if not table_found:
                    return {"error": f"AI suggested invalid table: {result['table_name']}"}
                
                # Clean up empty clauses
                if not result.get('where_clause') or result['where_clause'].strip() == '':
                    result['where_clause'] = '1=1'
                
                result['ai_parsed'] = True
                result['original_question'] = user_question
                
                return result
                
            except json.JSONDecodeError as e:
                return {"error": f"AI returned invalid JSON: {str(e)}", "ai_response": ai_response}
                
        except Exception as e:
            return {"error": f"AI parsing failed: {str(e)}"}
    
    def parse_user_query(self, user_question: str) -> Dict[str, Any]:
        """Main parsing method - tries AI first, falls back to rules"""
        if self.use_ai:
            import asyncio
            try:
                # Try AI parsing first
                ai_result = asyncio.run(self.parse_with_ai(user_question))
                
                if 'error' not in ai_result and ai_result.get('confidence', 0) >= 0.7:
                    return ai_result
                else:
                    print(f"AI parsing failed or low confidence: {ai_result.get('error', 'Low confidence')}")
            except Exception as e:
                print(f"AI parsing error: {str(e)}")
        
        # Fallback to rule-based parsing
        return self.fallback_rule_based_parsing(user_question)
    
    def fallback_rule_based_parsing(self, user_question: str) -> Dict[str, Any]:
        """Simplified rule-based fallback"""
        # This is a simplified version of the original parser
        # You can import and use the original QueryParser here
        
        enabled_tables = self.schema_loader.get_enabled_tables()
        if not enabled_tables:
            return {"error": "No enabled tables found"}
        
        # Simple table selection
        query_lower = user_question.lower()
        table_name = None
        
        for table_key, table_info in enabled_tables.items():
            if any(keyword in query_lower for keyword in ['product', 'customer', 'usage']):
                table_name = table_info.name
                break
        
        if not table_name:
            table_name = list(enabled_tables.values())[0].name
        
        # Simple column selection
        table_info = self.schema_loader.get_table_info(table_name)
        if table_info:
            columns = ['Month', 'Product', 'RequestCount']
            columns = [col for col in columns if col in table_info.columns]
            if not columns:
                columns = table_info.columns[:3]
        else:
            columns = ['*']
        
        # Simple WHERE clause
        where_clause = "1=1"
        if 'this month' in query_lower:
            where_clause = "Month LIKE '2025-08%'"
        
        # Simple ORDER clause
        order_clause = ""
        if 'top' in query_lower:
            order_clause = "ORDER BY RequestCount DESC"
        
        # Simple LIMIT clause
        limit_clause = ""
        top_match = re.search(r'top\s+(\d+)', query_lower)
        if top_match:
            limit_clause = f"TOP {top_match.group(1)}"
        
        return {
            'table_name': table_name,
            'columns': columns,
            'where_clause': where_clause,
            'order_clause': order_clause,
            'limit_clause': limit_clause,
            'ai_parsed': False,
            'fallback_used': True
        }


# Example configuration for different AI providers
AI_CONFIGS = {
    'openai': {
        'openai_api_key': 'your-openai-api-key',
        'model': 'gpt-3.5-turbo'
    },
    'azure_openai': {
        'openai_api_key': 'your-azure-openai-key',
        'openai_api_base': 'https://your-resource.openai.azure.com/',
        'openai_api_version': '2023-05-15',
        'model': 'gpt-35-turbo'
    }
}
