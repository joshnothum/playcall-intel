from playcall_intel.llm_client import MockLLMClient, LLMClient
from playcall_intel.ollama_client import OllamaClient
from playcall_intel.settings import get_settings


def get_llm_client() -> LLMClient:
    """
    Select the active LLM implementation from Settings.

    - mock → deterministic tests / zero cost
    - ollama → local llama3.1:8b
    """
    s = get_settings()

    if s.llm_provider == "ollama":
        return OllamaClient(
            model=s.ollama_model,
            base_url=s.ollama_base_url,
        )

    return MockLLMClient(
        fixed_play_type="other",
        fixed_result="other",
        fixed_yards_gained=None,
    )
