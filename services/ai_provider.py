"""
Central AI Provider Handler
Supports: openai (OpenAI-compatible APIs including SathiAI), g4f (GPT4Free)
Provider is controlled by DB setting 'AI_PROVIDER' or env var AI_PROVIDER.
"""
import os
import httpx
from typing import Dict, Any, List, Optional
from services.settings_service import get_setting_secure


class AIProviderBase:
    """Base class for AI providers"""

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    async def health_check(self) -> Dict[str, Any]:
        raise NotImplementedError


class OpenAIProvider(AIProviderBase):
    """OpenAI-compatible provider (works with SathiAI, OpenAI, or any compatible endpoint)"""

    def __init__(self):
        self.api_key = get_setting_secure(
            'SATHI_AI_API_KEY',
            os.getenv('OPENAI_API_KEY', '')
        )
        self.base_url = get_setting_secure(
            'SATHI_AI_BASE_URL',
            os.getenv('OPENAI_BASE_URL', 'https://sathiaiapi.ashlya.com/v1')
        )
        self.default_model = get_setting_secure('AI_MODEL', os.getenv('AI_MODEL', 'gpt-4'))
        self.timeout = 60.0

    def _reload_config(self):
        """Reload config from DB/env in case settings changed"""
        self.api_key = get_setting_secure(
            'SATHI_AI_API_KEY',
            os.getenv('OPENAI_API_KEY', '')
        )
        self.base_url = get_setting_secure(
            'SATHI_AI_BASE_URL',
            os.getenv('OPENAI_BASE_URL', 'https://sathiaiapi.ashlya.com/v1')
        )
        self.default_model = get_setting_secure('AI_MODEL', os.getenv('AI_MODEL', 'gpt-4'))

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> Dict[str, Any]:
        self._reload_config()
        use_model = model or self.default_model

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": use_model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": False
                }
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "content": data['choices'][0]['message']['content'],
                    "model": data.get('model', use_model),
                    "provider": "openai",
                    "provider_detail": self.base_url,
                }
            else:
                error_text = response.text[:200]
                raise Exception(f"OpenAI API returned {response.status_code}: {error_text}")

    async def health_check(self) -> Dict[str, Any]:
        self._reload_config()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                return {
                    "status": "operational" if response.status_code == 200 else "error",
                    "provider": "openai",
                    "endpoint": self.base_url
                }
        except Exception as e:
            return {"status": "error", "provider": "openai", "error": str(e)}


class G4FProvider(AIProviderBase):
    """GPT4Free (g4f) provider — uses g4f.client.AsyncClient"""

    def __init__(self):
        self.default_model = get_setting_secure('AI_MODEL', os.getenv('AI_MODEL', 'gpt-4o-mini'))

    def _reload_config(self):
        self.default_model = get_setting_secure('AI_MODEL', os.getenv('AI_MODEL', 'gpt-4o-mini'))

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> Dict[str, Any]:
        self._reload_config()
        use_model = model or self.default_model

        try:
            from g4f.client import AsyncClient

            client = AsyncClient()
            response = await client.chat.completions.create(
                model=use_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            content = response.choices[0].message.content
            returned_model = getattr(response, 'model', use_model) or use_model

            return {
                "success": True,
                "content": content,
                "model": returned_model,
                "provider": "g4f",
                "provider_detail": "GPT4Free",
            }
        except ImportError:
            raise Exception("g4f package is not installed. Install with: pip install -U g4f[all]")

    async def health_check(self) -> Dict[str, Any]:
        try:
            from g4f.client import AsyncClient
            client = AsyncClient()
            response = await client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5,
            )
            return {
                "status": "operational" if response.choices else "error",
                "provider": "g4f",
                "model": self.default_model,
            }
        except Exception as e:
            return {"status": "error", "provider": "g4f", "error": str(e)}


# ---------------------------------------------------------------------------
# Central handler — resolves provider from DB/env and delegates
# ---------------------------------------------------------------------------

_providers: Dict[str, AIProviderBase] = {}


def _get_provider_instance(name: str) -> AIProviderBase:
    """Get or create a cached provider instance"""
    if name not in _providers:
        if name == "openai":
            _providers[name] = OpenAIProvider()
        elif name == "g4f":
            _providers[name] = G4FProvider()
        else:
            raise ValueError(f"Unknown AI provider: {name}. Use 'openai' or 'g4f'.")
    return _providers[name]


def get_active_provider_name() -> str:
    """Return the currently configured provider name from DB or env"""
    return get_setting_secure('AI_PROVIDER', os.getenv('AI_PROVIDER', 'openai'))


def get_provider(provider_name: str = None) -> AIProviderBase:
    """
    Get the active AI provider instance.
    If provider_name is given, use that. Otherwise resolve from DB/env.
    """
    name = (provider_name or get_active_provider_name()).strip().lower()
    return _get_provider_instance(name)


async def chat_completion(
    messages: List[Dict[str, str]],
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = 500,
    provider_name: str = None,
    max_retries: int = 2,
) -> Dict[str, Any]:
    """
    Central chat completion function with retry logic.
    All AI calls across the app should go through this.
    """
    provider = get_provider(provider_name)

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            result = await provider.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            result["attempt"] = attempt
            return result
        except Exception as e:
            last_error = e
            print(f"[AI Provider] Attempt {attempt}/{max_retries} failed ({provider.__class__.__name__}): {e}")

    return {
        "success": False,
        "content": "I apologize, but I'm having connection issues. Please try again.",
        "error": str(last_error),
        "provider": get_active_provider_name() + " (error)",
        "attempt": max_retries,
    }


async def health_check(provider_name: str = None) -> Dict[str, Any]:
    """Health check for the active (or specified) provider"""
    provider = get_provider(provider_name)
    return await provider.health_check()
