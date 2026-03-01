"""
Curated list of working g4f models, based on community-verified data.
Updated from: https://github.com/xtekky/gpt4free

These models are known to work reliably with g4f. The list is organized by
category to allow the admin panel to present a model picker dropdown.
"""

# Text models — verified working via various providers
G4F_TEXT_MODELS = [
    {"id": "gpt-4o-mini", "label": "GPT-4o Mini", "provider": "auto", "default": True},
    {"id": "gpt-4o", "label": "GPT-4o", "provider": "auto"},
    {"id": "gpt-4", "label": "GPT-4", "provider": "auto"},
    {"id": "gpt-3.5-turbo", "label": "GPT-3.5 Turbo", "provider": "auto"},
    {"id": "gemini-2.5-flash", "label": "Gemini 2.5 Flash", "provider": "auto"},
    {"id": "gemini-2.0-flash", "label": "Gemini 2.0 Flash", "provider": "auto"},
    {"id": "claude-sonnet-4-5", "label": "Claude Sonnet 4.5", "provider": "auto"},
    {"id": "deepseek-v3", "label": "DeepSeek V3", "provider": "auto"},
    {"id": "deepseek-r1", "label": "DeepSeek R1", "provider": "auto"},
    {"id": "qwen-3-235b", "label": "Qwen 3 235B", "provider": "auto"},
    {"id": "llama-3.3-70b", "label": "Llama 3.3 70B", "provider": "auto"},
    {"id": "llama-3.1-405b", "label": "Llama 3.1 405B", "provider": "auto"},
    {"id": "grok-3", "label": "Grok 3", "provider": "auto"},
    {"id": "grok-3-mini", "label": "Grok 3 Mini", "provider": "auto"},
    {"id": "phi-4", "label": "Phi-4 (Microsoft)", "provider": "auto"},
    {"id": "command-a", "label": "Command A (Cohere)", "provider": "auto"},
]

# Image generation models
G4F_IMAGE_MODELS = [
    {"id": "flux", "label": "FLUX (Black Forest Labs)", "provider": "auto"},
    {"id": "flux-pro", "label": "FLUX Pro", "provider": "auto"},
    {"id": "gpt-image", "label": "GPT Image", "provider": "auto"},
    {"id": "dall-e-3", "label": "DALL-E 3", "provider": "auto"},
    {"id": "stable-diffusion-xl", "label": "Stable Diffusion XL", "provider": "auto"},
    {"id": "midjourney", "label": "Midjourney", "provider": "auto"},
]

# Vision-capable models (image input)
G4F_VISION_MODELS = [
    {"id": "gpt-4o", "label": "GPT-4o (Vision)", "provider": "auto"},
    {"id": "gpt-4o-mini", "label": "GPT-4o Mini (Vision)", "provider": "auto"},
    {"id": "gemini-2.0-flash", "label": "Gemini 2.0 Flash (Vision)", "provider": "auto"},
    {"id": "llama-3.2-90b", "label": "Llama 3.2 90B (Vision)", "provider": "auto"},
]


def get_all_models():
    """Return all model categories and lists for admin UI."""
    return {
        "text": G4F_TEXT_MODELS,
        "image": G4F_IMAGE_MODELS,
        "vision": G4F_VISION_MODELS,
    }


def get_default_model():
    """Return the default text model ID."""
    for m in G4F_TEXT_MODELS:
        if m.get("default"):
            return m["id"]
    return "gpt-4o-mini"
