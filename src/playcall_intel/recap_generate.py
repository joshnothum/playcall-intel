import json
from playcall_intel.recap_contract import GameRecapV1
from playcall_intel.recap_prompting import build_game_recap_prompt_v1


def generate_game_recap_v1(bs, highlights, client) -> GameRecapV1:
    prompt = build_game_recap_prompt_v1(bs, highlights)
    raw_json = client.complete_json(prompt)
    data = json.loads(raw_json)
    return GameRecapV1(**data)
