"""
AI Service - Central AI client using pluggable providers (openai / g4f)
Provider is selected via DB setting 'AI_PROVIDER' or env var AI_PROVIDER.
"""
from services import ai_provider
from typing import Optional, List, Dict, Any


class AIService:
    """AI Service using pluggable provider backend"""
    
    def __init__(self):
        self.default_model = None   # resolved by ai_provider from DB/env
        self.max_tokens = 500
        self.temperature = 0.7
        
    def build_system_prompt(self, page_type: str = 'general', page_data: Dict = None) -> str:
        """Build context-aware system prompt with actual data"""
        import json
        
        base_prompt = """You are Pearto AI, the intelligent assistant for Pearto Finance - a comprehensive financial platform. 
Your name is Pearto. Provide helpful, accurate, and professional financial guidance. Be concise and actionable.

Format your response with clean, readable markdown:
- Use ## for section headers (2-3 sections max)
- Use **bold** for key numbers and important terms
- Use bullet points (•) for lists
- Keep paragraphs short (2-3 sentences)
- Be concise but insightful (150-250 words max)
- Focus on actionable insights, not just listing data back"""
        
        # Add data context based on page type
        if page_data and isinstance(page_data, dict) and len(page_data) > 0:
            try:
                # Truncate large data to avoid token limits
                data_str = json.dumps(page_data, default=str)
                if len(data_str) > 3000:
                    data_str = data_str[:3000] + "... (truncated)"
                
                base_prompt += f"\n\n=== PAGE CONTEXT: {page_type.upper()} ===\n"
                base_prompt += f"Analyze and provide insights on this real-time data:\n{data_str}"
                
            except Exception as e:
                base_prompt += f"\n\nCONTEXT: {page_type} page data available"
        elif page_type == 'stock' and page_data:
            base_prompt += f"\n\nCONTEXT: Stock {page_data.get('symbol', 'N/A')} - Price: ${page_data.get('price', 'N/A')}"
        elif page_type == 'crypto' and page_data:
            base_prompt += f"\n\nCONTEXT: Cryptocurrency {page_data.get('symbol', 'N/A')}"
        elif page_type == 'portfolio':
            base_prompt += "\n\nCONTEXT: Wealth management portfolio"
        elif page_type == 'news':
            base_prompt += "\n\nCONTEXT: Financial news analysis"
        else:
            base_prompt += "\n\nCONTEXT: General financial platform"
            
        base_prompt += "\n\n❗ DISCLAIMER: This is AI-generated content, not professional financial advice."
        return base_prompt
    
    async def chat(
        self, 
        message: str, 
        context: Dict = None,
        options: Dict = None
    ) -> Dict[str, Any]:
        """
        Chat with AI service via the central provider
        """
        context = context or {}
        options = options or {}
        
        # Handle both camelCase (from frontend) and snake_case
        page_type = context.get('pageType') or context.get('page_type', 'general')
        page_data = context.get('pageData') or context.get('page_data', {})
        history = context.get('history', [])
        
        system_prompt = self.build_system_prompt(page_type, page_data)
        
        messages = [
            {"role": "system", "content": system_prompt},
            *history[-4:],  # Keep last 4 messages for context
            {"role": "user", "content": message}
        ]
        
        result = await ai_provider.chat_completion(
            messages=messages,
            model=options.get('model', self.default_model),
            temperature=options.get('temperature', self.temperature),
            max_tokens=options.get('max_tokens', self.max_tokens),
        )

        # Map to the response format the rest of the app expects
        return {
            "success": result.get("success", False),
            "response": result.get("content", ""),
            "provider": result.get("provider", "unknown"),
            "model": result.get("model", ""),
            "attempt": result.get("attempt", 1),
            **({"error": result["error"]} if "error" in result else {}),
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Check AI service status via the active provider"""
        return await ai_provider.health_check()


# Singleton instance
ai_service = AIService()
