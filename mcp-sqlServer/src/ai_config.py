"""
AI Configuration for enhanced query parsing
"""

# Configuration for different AI parsing options
AI_PARSING_CONFIGS = {
    # Option 1: Use local AI model (Ollama)
    "local_ai_only": {
        "use_ai": True,
        "ai_type": "local",
        "local_ai": {
            "model": "llama3.1:8b",  # or codellama:7b, mistral:7b
            "base_url": "http://localhost:11434",
            "timeout": 30
        }
    },
    
    # Option 2: Use cloud AI (OpenAI/Azure OpenAI)
    "cloud_ai_only": {
        "use_ai": True,
        "ai_type": "cloud",
        "cloud_ai": {
            "openai_api_key": "your-api-key-here",
            "model": "gpt-3.5-turbo",
            # For Azure OpenAI, also include:
            # "openai_api_base": "https://your-resource.openai.azure.com/",
            # "openai_api_version": "2023-05-15"
        }
    },
    
    # Option 3: Hybrid approach (try local first, fallback to cloud)
    "hybrid_ai": {
        "use_ai": True,
        "ai_type": "hybrid",
        "local_ai": {
            "model": "llama3.1:8b",
            "base_url": "http://localhost:11434",
            "timeout": 15  # Shorter timeout for quick fallback
        },
        "cloud_ai": {
            "openai_api_key": "your-api-key-here",
            "model": "gpt-3.5-turbo"
        }
    },
    
    # Option 4: Disable AI (use original rule-based parsing)
    "rule_based_only": {
        "use_ai": False
    }
}

# Example of how to use the configuration
def get_ai_config(config_name: str = "rule_based_only"):
    """Get AI configuration by name"""
    return AI_PARSING_CONFIGS.get(config_name, AI_PARSING_CONFIGS["rule_based_only"])

# Instructions for setting up local AI (Ollama)
OLLAMA_SETUP_INSTRUCTIONS = """
To use local AI parsing with Ollama:

1. Install Ollama: https://ollama.ai/download
2. Pull a model:
   ollama pull llama3.1:8b
   # or
   ollama pull codellama:7b
   
3. Start Ollama service:
   ollama serve
   
4. Test the model:
   ollama run llama3.1:8b "Hello, world!"

5. Update your configuration to use "local_ai_only" or "hybrid_ai"
"""

# Instructions for cloud AI setup
CLOUD_AI_SETUP_INSTRUCTIONS = """
To use cloud AI parsing:

1. For OpenAI:
   - Get API key from https://platform.openai.com/
   - Set in config: "openai_api_key": "sk-..."
   
2. For Azure OpenAI:
   - Create Azure OpenAI resource
   - Deploy a model (gpt-35-turbo recommended)
   - Get endpoint, API key, and API version
   - Update config with Azure-specific settings

3. Install required package:
   pip install openai

4. Update your configuration to use "cloud_ai_only" or "hybrid_ai"
"""
