from typing import Any, Dict, Optional

from playcall_intel.schema import Play


def _to_int(value: Any) -> Optional[int]:
    """
    Normalize mixed nflverse numeric fields into a clean int

    - Handles the messy reality: None, empty strings, 'NaN', and float-like values
    - Converts everything through float → int because many csv fields arrive as '10.0'
    - Returns None instead of raising so the pipeline can decide how to default or validate
    """
    if value is None:
        return None

    s = str(value).strip()

    if s == "" or s.lower() == "none" or s.lower() == "nan":
        return None

    try:
        return int(float(s))
    except ValueError:
        return None

def is_scrimmage_play(row: Dict[str, Any]) -> bool:
    """
    Decide whether a row looks like a standard offensive snap

    - Filters out kickoffs / transitions where down & distance are not defined
    - Keeps the first-pass mapper focused on the common case we want to normalize
    - This rule will evolve as we learn edge cases (penalties, no-plays, etc.)
    """
    return bool(row.get("posteam")) and _to_int(row.get("down")) is not None and _to_int(row.get("ydstogo")) is not None

def row_to_play_first_pass(row: Dict[str, Any]) -> Play:
    """
    First-pass mapping from nflverse pbp row → Play

    - Start with fields that map cleanly and exist consistently (teams, down/distance, yardline_100)
    - Leave play_type/result as placeholders until we define a normalization taxonomy
    - Creates real-data objects we can validate before bringing the LLM into the loop
    """
    offense = row.get("posteam") or ""
    defense = row.get("defteam") or ""

    return Play(
        offense_team=offense,
        defense_team=defense,
        quarter=_to_int(row.get("qtr")) or 0, # first pass keeps Play fully populated; validation rules come later
        down=_to_int(row.get("down")) or 0,
        distance=_to_int(row.get("ydstogo")) or 0,
        yardline_100=_to_int(row.get("yardline_100")) or 0,
        play_type="unknown",  # TODO: define taxonomy + map (or LLM-normalize) from play_type/desc
        yards_gained=_to_int(row.get("yards_gained")),
        result=None,  # TODO: define result categories; may come from desc/penalty fields
    )
