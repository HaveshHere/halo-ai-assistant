from settings import get_ai_provider, get_ollama_base_url, get_recommended_model


def ai_status():
    provider = get_ai_provider().lower()
    model = get_recommended_model()

    if provider == "ollama":
        return f"AI reasoning uses Ollama with model {model} at {get_ollama_base_url()}."

    return f"AI provider is set to {provider}. Supported Phase 2 provider: ollama."