import json

from playcall_intel.llm_client import LLMClient
from playcall_intel.llm_contract import LLMNormalizationV1
from playcall_intel.prompting import build_prompt_v1
from playcall_intel.schema import Play


def normalize_with_llm_v1(play: Play, client: LLMClient) -> LLMNormalizationV1:
    """
    LLM-assisted normalization pass (v1)

    - Build a deterministic JSON-only prompt from the Play object
    - Validate the model output against a strict contract before using it
    - Keeps AI output as data, not free-form text
    """
    prompt = build_prompt_v1(play)
    raw_json = client.complete_json(prompt)

    data = json.loads(raw_json)
    return LLMNormalizationV1(**data)
