import json
from typing import Any


def build_game_recap_prompt_v1(bs: Any, highlights: list[str]) -> str:

    payload = {
        "task": "Write ONLY valid JSON with keys: paragraph_1, paragraph_2. No extra keys.",
        "rules": [
            "Use ONLY the facts in the stats and highlights below.",
            "Do NOT invent players, scores, records, or events not listed.",
            "Keep each paragraph 4-6 sentences. Be excited, like it was the greatest game you ever saw.",
        ],
        "stats": {
            "game_id": bs.game_id,
            "home_team": bs.home_team,
            "away_team": bs.away_team,
            "home_score": bs.home_score,
            "away_score": bs.away_score,
            "home_off_plays": bs.home_off_plays,
            "away_off_plays": bs.away_off_plays,
            "home_off_yards": bs.home_total_yards,
            "away_off_yards": bs.away_total_yards,
            "home_pass": bs.home_pass,
            "home_run": bs.home_run,
            "away_pass": bs.away_pass,
            "away_run": bs.away_run,
            "home_turnovers": bs.home_turnovers,
            "away_turnovers": bs.away_turnovers,
            "home_sacks": bs.home_sacks,
            "away_sacks": bs.away_sacks,
        },
        "highlights": highlights[:12],
        "example_output": {
            "paragraph_1": "…",
            "paragraph_2": "…",
        },
    }
    return json.dumps(payload, ensure_ascii=False)
