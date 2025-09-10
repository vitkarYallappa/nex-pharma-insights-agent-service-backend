"""
Agent Configuration for Stage1 Orchestrator

Easy configuration to enable/disable agents using environment variables
"""

import os
from typing import Dict, Any

def _get_env_bool(env_var: str, default: bool = False) -> bool:
    """Get boolean value from environment variable"""
    value = os.getenv(env_var, str(default)).lower()
    return value in ('true', '1', 'yes', 'on', 'enabled')

# Agent Enable/Disable Configuration from Environment Variables
AGENT_CONFIG = {
    "agent1_deduplication": {
        "enabled": _get_env_bool("AGENT1_DEDUPLICATION_ENABLED", False),
        "name": "Deduplication Agent",
        "description": "Identifies and removes duplicate content",
        "env_var": "AGENT1_DEDUPLICATION_ENABLED"
    },
    "agent2_relevance": {
        "enabled": _get_env_bool("AGENT2_RELEVANCE_ENABLED", False),
        "name": "Relevance Agent", 
        "description": "Scores content relevance and categorizes",
        "env_var": "AGENT2_RELEVANCE_ENABLED"
    },
    "agent3_insights": {
        "enabled": _get_env_bool("AGENT3_INSIGHTS_ENABLED", True),
        "name": "Insights Agent",
        "description": "Generates insights from content",
        "env_var": "AGENT3_INSIGHTS_ENABLED"
    },
    "agent4_implications": {
        "enabled": _get_env_bool("AGENT4_IMPLICATIONS_ENABLED", True),
        "name": "Implications Agent",
        "description": "Identifies business implications",
        "env_var": "AGENT4_IMPLICATIONS_ENABLED"
    }
}

def get_enabled_agents():
    """Get list of enabled agent types"""
    return [
        agent_key for agent_key, config in AGENT_CONFIG.items() 
        if config.get("enabled", False)
    ]

def is_agent_enabled(agent_key: str) -> bool:
    """Check if specific agent is enabled"""
    return AGENT_CONFIG.get(agent_key, {}).get("enabled", False)

def get_agent_info(agent_key: str) -> dict:
    """Get agent information"""
    return AGENT_CONFIG.get(agent_key, {})

def print_agent_status():
    """Print current agent status"""
    print("🔧 Stage1 Agent Configuration:")
    print("=" * 50)
    
    for agent_key, config in AGENT_CONFIG.items():
        status = "✅ ENABLED" if config["enabled"] else "❌ DISABLED"
        env_value = os.getenv(config["env_var"], "not set")
        print(f"{config['name']}: {status}")
        print(f"   {config['description']}")
        print(f"   Environment: {config['env_var']}={env_value}")
        print()
    
    enabled_count = len(get_enabled_agents())
    total_count = len(AGENT_CONFIG)
    print(f"📊 Summary: {enabled_count}/{total_count} agents enabled")
    print()
    print("💡 To enable/disable agents, set environment variables:")
    for agent_key, config in AGENT_CONFIG.items():
        status = "true" if config["enabled"] else "false"
        print(f"   export {config['env_var']}={status}")

def create_env_file_template():
    """Create .env file template"""
    env_content = """# Stage1 Agent Configuration
# Set to 'true' or 'false' to enable/disable agents

# Agent1: Deduplication (removes duplicate content)
AGENT1_DEDUPLICATION_ENABLED=false

# Agent2: Relevance (scores content relevance)
AGENT2_RELEVANCE_ENABLED=false

# Agent3: Insights (generates insights from content)
AGENT3_INSIGHTS_ENABLED=true

# Agent4: Implications (identifies business implications)
AGENT4_IMPLICATIONS_ENABLED=true

# API Keys for Agent Services
# PERPLEXITY_API_KEY=your_key_here
# SERP_API_KEY=your_key_here

# Agent 3 Insights - Anthropic Claude API Keys
# Choose one or both providers:
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
# AWS_REGION=us-east-1  # For AWS Bedrock (also set AWS credentials)
"""
    
    print("📄 .env File Template:")
    print("=" * 30)
    print(env_content)
    
    # Optionally write to file
    try:
        with open(".env.template", "w") as f:
            f.write(env_content)
        print("✅ Template saved as .env.template")
        print("💡 Copy to .env and modify as needed:")
        print("   cp .env.template .env")
    except Exception as e:
        print(f"❌ Could not save template: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "template":
        create_env_file_template()
    else:
        print_agent_status() 