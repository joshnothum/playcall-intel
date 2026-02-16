from dataclasses import dataclass
from functools import lru_cache
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    """
    Central configuration for the project

    - Keeps environment-specific values out of the code
    - Lets the pipeline switch between mock and local LLM without edits
    - Gives a single source of truth for paths and runtime behavior
    """

    # Core project
    project_name: str = "playcall-intel"
    environment: str = "dev"

    # Data paths
    data_dir: str = "data"
    raw_data_dir: str = "data/raw"
    processed_data_dir: str = "data/processed"

    # LLM runtime selection
    llm_provider: str = "mock"

    # Ollama (local LLaMA)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"


@lru_cache
def get_settings() -> Settings:
    """
    Read settings from environment variables (with defaults)

    Cached so the same config is reused across the app.
    """
    return Settings(
        project_name=os.getenv("PROJECT_NAME", "playcall-intel"),
        environment=os.getenv("ENVIRONMENT", "dev"),

        data_dir=os.getenv("DATA_DIR", "data"),
        raw_data_dir=os.getenv("RAW_DATA_DIR", "data/raw"),
        processed_data_dir=os.getenv("PROCESSED_DATA_DIR", "data/processed"),

        llm_provider=os.getenv("LLM_PROVIDER", "mock"),

        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
    )
