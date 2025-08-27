"""
AI-powered query parser using local models (Ollama, etc.)
"""
import json
import re
import requests
from typing import Any, Dict, List, Optional
from .models import QueryInfo
from .schema_loader import SchemaLoader


class LocalAIQueryParser:
    """AI-powered query parser using local AI models like Ollama"""
    
    def __init__(self, schema_loader: SchemaLoader, ai_config: Optional[Dict] = None):
        self.schema_loader = schema_loader
        self.ai_config = ai_config or {
            'model': 'llama3.1:8b',  # or 'codellama', 'mistral', etc.
            'base_url': 'http://localhost:11434',
            'timeout': 30
        }
    
    def get_schema_context(self) -> str:
        """Generate concise schema context for AI model"""
        enabled_tables = self.schema_loader.get_enabled_tables()
        schema_info = []
        
        for table_key, table_info in enabled_tables.items():
            # Create concise table description
            columns_with_types = []
            for col in table_info.columns:
                col_desc = col
                if col in table_info.column_metadata:
                    meta = table_info.column_metadata[col]
                    if meta.get('enum'):
                        col_desc += f"({','.join(meta['enum'][:3])}...)"
                columns_with_types.append(col_desc)
            
            table_desc = f"{table_info.name}: {table_info.description} | Columns: {', '.join(columns_with_types)}"
            schema_info.append(table_desc)
        
        return " | ".join(schema_info)
    
    def create_prompt(self, user_question: str) -> str:
        """Create concise prompt for local AI model"""
        schema_context = self.get_schema_context()
        
        prompt = f"""Convert this natural language question to SQL components.

Schema: {schema_context}

Question: "{user_question}"

Respond with only JSON:
{{
    "table_name": "table name",
    "columns": ["col1", "col2"],
    "where_clause": "conditions without WHERE",
    "order_clause": "ORDER BY clause or empty",
    "limit_clause": "TOP N or empty"
}}

Rules:
- Use TOP N for "top N" requests
- Use LIKE for partial date matches
- Include RequestCount, Month when relevant
- Empty string for unused clauses"""

        return prompt
    
    async def query_local_ai(self, prompt: str) -> str:
        """Query local AI model (Ollama)"""
        try:
            url = f"{self.ai_config['base_url']}/api/generate"
            
            data = {
                "model": self.ai_config['model'],
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_predict": 500
                }
            }
            
            response = requests.post(
                url, 
                json=data, 
                timeout=self.ai_config['timeout']
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to query local AI: {str(e)}")
        except Exception as e:
            raise Exception(f"Local AI error: {str(e)}")
    
    def extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON from AI response, handling various formats"""
        # Try to find JSON in the response
        json_patterns = [
            r'\{[^}]*\}',  # Simple JSON
            r'\{.*?\}',    # JSON with nested content
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        # If no JSON found, try to parse the whole response
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            # If still fails, create structured response from text
            return self.parse_text_response(response)
    
    def parse_text_response(self, response: str) -> Dict[str, Any]:
        """Parse non-JSON response into structured format"""
        lines = response.lower().split('\n')
        result = {
            'table_name': '',
            'columns': [],
            'where_clause': '1=1',
            'order_clause': '',
            'limit_clause': ''
        }
        
        # Simple text parsing fallback
        enabled_tables = self.schema_loader.get_enabled_tables()
        for table_key, table_info in enabled_tables.items():
            if table_info.name.lower() in response.lower():
                result['table_name'] = table_info.name
                result['columns'] = ['Month', 'Product', 'RequestCount']
                break
        
        if not result['table_name'] and enabled_tables:
            first_table = list(enabled_tables.values())[0]
            result['table_name'] = first_table.name
            result['columns'] = first_table.columns[:3]
        
        return result
    
    async def parse_with_ai(self, user_question: str) -> Dict[str, Any]:
        """Parse user question using local AI model"""
        try:
            prompt = self.create_prompt(user_question)
            ai_response = await self.query_local_ai(prompt)
            
            # Extract structured data from response
            result = self.extract_json_from_response(ai_response)
            
            # Validate and clean up result
            result = self.validate_and_clean_result(result, user_question)
            
            return result
            
        except Exception as e:
            return {"error": f"AI parsing failed: {str(e)}"}
    
    def validate_and_clean_result(self, result: Dict[str, Any], user_question: str) -> Dict[str, Any]:
        """Validate and clean up AI parsing result"""
        # Ensure required fields exist
        required_fields = ['table_name', 'columns', 'where_clause', 'order_clause', 'limit_clause']
        for field in required_fields:
            if field not in result:
                result[field] = '' if field != 'columns' else []
        
        # Validate table exists
        enabled_tables = self.schema_loader.get_enabled_tables()
        table_found = False
        for table_key, table_info in enabled_tables.items():
            if table_info.name == result['table_name']:
                table_found = True
                break
        
        if not table_found and enabled_tables:
            # Fallback to first available table
            first_table = list(enabled_tables.values())[0]
            result['table_name'] = first_table.name
            if not result['columns']:
                result['columns'] = first_table.columns[:3]
        
        # Clean up empty clauses
        if not result['where_clause'] or result['where_clause'].strip() == '':
            result['where_clause'] = '1=1'
        
        # Ensure columns is a list
        if isinstance(result['columns'], str):
            result['columns'] = [col.strip() for col in result['columns'].split(',')]
        
        # Add metadata
        result['ai_parsed'] = True
        result['original_question'] = user_question
        result['ai_model'] = self.ai_config['model']
        
        return result
    
    def parse_user_query(self, user_question: str) -> Dict[str, Any]:
        """Main parsing method"""
        import asyncio
        
        try:
            # Try AI parsing
            result = asyncio.run(self.parse_with_ai(user_question))
            
            if 'error' in result:
                print(f"AI parsing failed: {result['error']}")
                return self.fallback_parsing(user_question)
            
            return result
            
        except Exception as e:
            print(f"AI parsing error: {str(e)}")
            return self.fallback_parsing(user_question)
    
    def fallback_parsing(self, user_question: str) -> Dict[str, Any]:
        """Simple rule-based fallback"""
        enabled_tables = self.schema_loader.get_enabled_tables()
        if not enabled_tables:
            return {"error": "No enabled tables found"}
        
        # Use first available table
        first_table = list(enabled_tables.values())[0]
        table_info = self.schema_loader.get_table_info(first_table.name)
        
        return {
            'table_name': first_table.name,
            'columns': table_info.columns[:5] if table_info else ['*'],
            'where_clause': '1=1',
            'order_clause': '',
            'limit_clause': '',
            'ai_parsed': False,
            'fallback_used': True,
            'original_question': user_question
        }


# Example usage configuration
LOCAL_AI_CONFIGS = {
    'ollama_llama': {
        'model': 'llama3.1:8b',
        'base_url': 'http://localhost:11434',
        'timeout': 30
    },
    'ollama_codellama': {
        'model': 'codellama:7b',
        'base_url': 'http://localhost:11434',
        'timeout': 30
    },
    'ollama_mistral': {
        'model': 'mistral:7b',
        'base_url': 'http://localhost:11434',
        'timeout': 30
    }
}
