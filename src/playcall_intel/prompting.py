import json
from playcall_intel.schema import Play


def build_prompt_v1(play: Play) -> str:
    """
    Build a deterministic prompt that asks for LLMNormalizationV1 JSON

    - Keep the instruction tight so output stays machine-parseable
    - Provide the structured baseline plus the raw play text
    - The goal is consistent JSON, not creative writing
    """
    schema_hint = {
        "play_type": "run|pass|qb_kneel|qb_spike|kickoff|punt|field_goal|extra_point|two_point_attempt|penalty|no_play|other",
        "result": "tackle|complete|incomplete|touchdown|interception|fumble|sack|out_of_bounds|penalty|no_play|other",
        "yards_gained": "integer or null",
    }

    payload = {
        "baseline": {
            "play_type": play.play_type,
            "result": play.result,
            "yards_gained": play.yards_gained,
            "down": play.down,
            "distance": play.distance,
            "yardline_100": play.yardline_100,
        },
        "play_text": play.play_text,
        "required_json_shape": schema_hint,
        "rules": [
            "Return ONLY valid JSON (no markdown, no commentary).",
            "Use only the allowed category values shown in required_json_shape.",
            "If unsure, choose 'other' for play_type or result, and null for yards_gained.",
        ],
    }

    return json.dumps(payload, ensure_ascii=False)
