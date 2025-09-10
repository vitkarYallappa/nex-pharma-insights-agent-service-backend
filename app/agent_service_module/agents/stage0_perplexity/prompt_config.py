"""
Prompt configuration for Perplexity content extraction
Easy to update for demos and different use cases
"""

class PromptConfig:
    """Configuration for Perplexity extraction prompts"""
    
    # Default prompts for MVP
    DEFAULT_SYSTEM_PROMPT = """Extract and summarize the main content from the provided URL. Focus on key information and insights."""
    
    DEFAULT_USER_PROMPT = "Extract content from: {url}"
    
    # Demo prompts - more detailed for presentations
    DEMO_SYSTEM_PROMPT = """You are an expert content analyst. Extract and summarize the main content from the provided URL.
    
Focus on:
- Key insights and main points
- Important data and statistics
- Actionable information
- Market trends or developments
    
Provide a clear, structured summary that highlights the most valuable information."""
    
    DEMO_USER_PROMPT = "Please analyze and extract the key content from this URL: {url}"
    
    # Detailed prompts - for comprehensive extraction
    DETAILED_SYSTEM_PROMPT = """You are a professional content extraction specialist. Your task is to thoroughly analyze and extract content from web pages.
    
Please extract:
1. Main topic and key themes
2. Important facts, data, and statistics
3. Key insights and conclusions
4. Relevant quotes or statements
5. Market implications or trends
6. Actionable information
    
Format your response with clear sections and bullet points where appropriate. Focus on accuracy and completeness while maintaining readability."""
    
    DETAILED_USER_PROMPT = "Perform a comprehensive content analysis and extraction from: {url}"
    
    # Quick prompts - for fast extraction
    QUICK_SYSTEM_PROMPT = "Extract the main points and key information from the URL content. Be concise and focus on the most important details."
    
    QUICK_USER_PROMPT = "Quick extract from: {url}"

class PromptManager:
    """Manages different prompt configurations"""
    
    PROMPT_TYPES = {
        "default": (PromptConfig.DEFAULT_SYSTEM_PROMPT, PromptConfig.DEFAULT_USER_PROMPT),
        "demo": (PromptConfig.DEMO_SYSTEM_PROMPT, PromptConfig.DEMO_USER_PROMPT),
        "detailed": (PromptConfig.DETAILED_SYSTEM_PROMPT, PromptConfig.DETAILED_USER_PROMPT),
        "quick": (PromptConfig.QUICK_SYSTEM_PROMPT, PromptConfig.QUICK_USER_PROMPT)
    }
    
    @staticmethod
    def get_prompts(prompt_type: str = "default") -> tuple[str, str]:
        """Get system and user prompts by type"""
        if prompt_type not in PromptManager.PROMPT_TYPES:
            prompt_type = "default"
        
        return PromptManager.PROMPT_TYPES[prompt_type]
    
    @staticmethod
    def get_system_prompt(prompt_type: str = "default") -> str:
        """Get system prompt by type"""
        system_prompt, _ = PromptManager.get_prompts(prompt_type)
        return system_prompt
    
    @staticmethod
    def get_user_prompt(prompt_type: str = "default") -> str:
        """Get user prompt template by type"""
        _, user_prompt = PromptManager.get_prompts(prompt_type)
        return user_prompt
    
    @staticmethod
    def format_user_prompt(url: str, prompt_type: str = "default") -> str:
        """Get formatted user prompt with URL"""
        user_prompt_template = PromptManager.get_user_prompt(prompt_type)
        return user_prompt_template.format(url=url) 