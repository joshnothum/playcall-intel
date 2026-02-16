from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()


@dataclass
class Settings:
    project_name: str = "playcall-intel"
    environment: str = os.getenv("ENVIRONMENT", "dev")

    # future model configuration
    model_name: str = os.getenv("MODEL_NAME", "local-llama")

    # data paths
    data_dir: str = "data"
    raw_data_dir: str = "data/raw"
    processed_data_dir: str = "data/processed"


settings = Settings()
