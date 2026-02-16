import json
from dataclasses import dataclass
from typing import Optional, Protocol

from playcall_intel.llm_contract import LLMNormalizationV1


class LLMClient(Protocol):
    """
    Minimal client interface for "get me JSON for this prompt"

    - Keeps the rest of the pipeline independent of any vendor SDK
    - Lets me swap in a real client later without changing business logic
    - Makes unit tests deterministic by using a mock client
    """

    def complete_json(self, prompt: str) -> str: ...


@dataclass
class MockLLMClient:
    """
    Deterministic stand-in for a real model call

    - Returns valid JSON that matches LLMNormalizationV1
    - Keeps demos/test runs predictable while plumbing evolves
    - Acts as the default until real model integration is added
    """

    fixed_play_type: str = "other"
    fixed_result: str = "other"
    fixed_yards_gained: Optional[int] = None

    def complete_json(self, prompt: str) -> str:
        # Prompt is intentionally unused in mock mode (determinism > realism)
        payload = {
            "play_type": self.fixed_play_type,
            "result": self.fixed_result,
            "yards_gained": self.fixed_yards_gained,
        }
        return json.dumps(payload)

    def complete_and_validate(self, prompt: str) -> LLMNormalizationV1:
        raw = self.complete_json(prompt)
        data = json.loads(raw)
        return LLMNormalizationV1(**data)
