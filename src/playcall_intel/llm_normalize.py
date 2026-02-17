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

def apply_llm_enrichment(play: Play, llm_out: LLMNormalizationV1) -> Play:
    """
    Merge contract-validated LLM output back onto the baseline Play.

    Design choice:
    - Keep the original Play immutable in spirit
    - Treat the LLM as a structured enrichment layer, not a source of truth
    """

    return Play(
        offense_team=play.offense_team,
        defense_team=play.defense_team,
        quarter=play.quarter,
        down=play.down,
        distance=play.distance,
        yardline_100=play.yardline_100,

        play_type=llm_out.play_type,
        result=llm_out.result,
        yards_gained=llm_out.yards_gained,

        play_text=play.play_text,
    )
