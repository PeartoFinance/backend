"""
AI Service - OpenAI-compatible client for SathiAI
"""
import os
import httpx
from typing import Optional, List, Dict, Any


class AIService:
    """AI Service using OpenAI-compatible API"""
    
    def __init__(self):
        self.api_key = os.getenv('SATHI_AI_API_KEY', 'sk-0mw9OdrHDBiYOE5VeEDyieB1IAk9imlBF3uQMXXCIh8Chmug')
        self.base_url = os.getenv('SATHI_AI_BASE_URL', 'https://sathiaiapi.ashlya.com/v1')
        self.default_model = 'gpt-4'
        self.max_tokens = 500
        self.temperature = 0.7
        self.timeout = 60.0
        
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
        Chat with AI service
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
        
        max_retries = 2
        for attempt in range(1, max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": options.get('model', self.default_model),
                            "messages": messages,
                            "temperature": options.get('temperature', self.temperature),
                            "max_tokens": options.get('max_tokens', self.max_tokens),
                            "stream": False
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        ai_message = data['choices'][0]['message']['content']
                        return {
                            "success": True,
                            "response": ai_message,
                            "provider": "SathiAI",
                            "model": data.get('model', self.default_model),
                            "attempt": attempt
                        }
                    else:
                        raise Exception(f"API returned {response.status_code}")
                        
            except Exception as e:
                print(f"[AI Service] Attempt {attempt}/{max_retries} failed: {e}")
                if attempt == max_retries:
                    return {
                        "success": False,
                        "response": "I apologize, but I'm having connection issues. Please try again.",
                        "error": str(e),
                        "provider": "SathiAI (error)"
                    }
        
        return {
            "success": False,
            "response": "Service unavailable.",
            "provider": "fallback"
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Check AI service status"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                return {
                    "status": "operational" if response.status_code == 200 else "error",
                    "provider": "SathiAI",
                    "endpoint": self.base_url
                }
        except Exception as e:
            return {
                "status": "error",
                "provider": "SathiAI",
                "error": str(e)
            }


# Singleton instance
ai_service = AIService()
