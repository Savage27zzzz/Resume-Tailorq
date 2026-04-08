import os
from openai import OpenAI

PROVIDERS = {
    "openai": {
        "base_url": None,
        "default_model": "gpt-4o",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "default_model": "gemini-2.0-flash",
    },
}


def get_client() -> OpenAI:
    """Create an OpenAI-compatible client based on AI_PROVIDER env var."""
    provider = os.environ.get("AI_PROVIDER", "openai").lower()

    if provider == "gemini":
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set. Add it to your .env file.")
        return OpenAI(
            api_key=api_key,
            base_url=PROVIDERS["gemini"]["base_url"],
        )
    else:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set. Add it to your .env file.")
        return OpenAI(api_key=api_key)


def get_default_model() -> str:
    """Get the default model for the current provider."""
    provider = os.environ.get("AI_PROVIDER", "openai").lower()
    model_override = os.environ.get("AI_MODEL") or os.environ.get("OPENAI_MODEL")
    if model_override:
        return model_override
    return PROVIDERS.get(provider, PROVIDERS["openai"])["default_model"]
