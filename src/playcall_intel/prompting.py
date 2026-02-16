from textwrap import dedent
from playcall_intel.schema import Play


def build_prompt_v1(play: Play) -> str:
    allowed_play_type = (
        "run|pass|qb_kneel|qb_spike|kickoff|punt|field_goal|extra_point|"
        "two_point_attempt|penalty|no_play|other"
    )
    allowed_result = (
        "tackle|complete|incomplete|touchdown|interception|fumble|sack|"
        "out_of_bounds|penalty|no_play|other"
    )
    allowed_direction = "left|middle|right|unknown"

    prompt = f"""
You are extracting a normalized label set from a football play description.

Return ONLY a single JSON object with EXACTLY these keys:
play_type
result
yards_gained
run_direction

Allowed values:
play_type: {allowed_play_type}
result: {allowed_result}
run_direction: {allowed_direction}
yards_gained: integer or null

Rules:
Use only allowed values.
For non-run plays, set run_direction to "unknown".
Output must be valid JSON. No markdown. No extra keys.

Play context (baseline):
play_type_baseline: {play.play_type}
result_baseline: {play.result}
yards_gained_baseline: {play.yards_gained}
down: {play.down}
distance: {play.distance}
yardline_100: {play.yardline_100}

Play text:
{play.play_text}

Example output:
{{"play_type":"run","result":"tackle","yards_gained":3,"run_direction":"right"}}

Now return the JSON object:
"""

    return dedent(prompt).strip()
