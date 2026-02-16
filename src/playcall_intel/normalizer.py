from playcall_intel.schema import Play


def normalize_manual(raw_play: dict) -> Play:
    """
    First end-to-end normalization path (no LLM yet)

    - Proves raw → Play transformation using the schema contract
    - Makes the schema executable (not just a design artifact)
    - Defines the interface the future LLM parser must satisfy
    """
    return Play(
        offense_team=raw_play["offense_team"],
        defense_team=raw_play["defense_team"],
        quarter=raw_play["quarter"],
        down=raw_play["down"],
        distance=raw_play["distance"],
        yardline_100=raw_play["yardline_100"],
        play_type=raw_play["play_type"],
        yards_gained=raw_play.get("yards_gained"),
        result=raw_play.get("result"),
    )
