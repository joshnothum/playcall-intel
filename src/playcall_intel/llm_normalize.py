import json

from playcall_intel.llm_client import LLMClient
from playcall_intel.llm_contract import LLMNormalizationV1
from playcall_intel.prompting import build_prompt_v1
from playcall_intel.schema import Play
from typing import Any, Dict
VALID_PLAY_TYPES = {
    "run", "pass", "qb_kneel", "qb_spike", "kickoff", "punt",
    "field_goal", "extra_point", "two_point_attempt", "penalty",
    "no_play", "other",
}

VALID_RESULTS = {
    "tackle", "complete", "incomplete", "touchdown", "interception",
    "fumble", "sack", "out_of_bounds", "penalty", "no_play", "other",
}


def repair_llm_output(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Small, conservative repair for common model mixups.

    Principle:
    - Fix only obvious field swaps (e.g., play_type='sack')
    - Do not invent new labels
    - Keep the output contract-valid so the batch pipeline keeps moving
    """
    # Common mixup: model puts a result label into play_type
    pt = data.get("play_type")
    res = data.get("result")

    if pt == "sack":
        data["play_type"] = "pass"
        if res not in VALID_RESULTS:
            data["result"] = "sack"

    # If play_type is invalid, degrade gracefully instead of crashing
    if data.get("play_type") not in VALID_PLAY_TYPES:
        data["play_type"] = "other"

    # If result is invalid, degrade gracefully
    if data.get("result") not in VALID_RESULTS:
        data["result"] = "other"

    return data

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
    data = repair_llm_output(data)
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
