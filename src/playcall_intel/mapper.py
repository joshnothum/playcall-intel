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
        play_type=infer_play_type(row),  # TODO: define taxonomy + map (or LLM-normalize) from play_type/desc
        play_text=row.get("desc") or "",
        yards_gained=_to_int(row.get("yards_gained")),
        result=infer_result(row),  # TODO: define result categories; may come from desc/penalty fields
    )
def infer_play_type(row: Dict[str, Any]) -> str:
    """
    First-pass play type classification from nflverse structured flags

    - Prefer explicit boolean fields over text parsing (fast + consistent)
    - Keep categories small and stable; detail can come later
    - Gives the LLM a clear target for ambiguous / text-only edge cases
    """
    # Administrative / non-plays
    if _to_int(row.get("no_play")) == 1:
        return "no_play"
    if _to_int(row.get("penalty")) == 1:
        return "penalty"

    # QB management plays
    if _to_int(row.get("qb_kneel")) == 1:
        return "qb_kneel"
    if _to_int(row.get("qb_spike")) == 1:
        return "qb_spike"

    # Special teams
    if _to_int(row.get("kickoff_attempt")) == 1:
        return "kickoff"
    if _to_int(row.get("punt_attempt")) == 1:
        return "punt"
    if _to_int(row.get("field_goal_attempt")) == 1:
        return "field_goal"
    if _to_int(row.get("extra_point_attempt")) == 1:
        return "extra_point"
    if _to_int(row.get("two_point_attempt")) == 1:
        return "two_point_attempt"

    # Core offense
    if _to_int(row.get("rush")) == 1:
        return "run"
    if _to_int(row.get("pass")) == 1:
        return "pass"

    return "other"

def infer_result(row: Dict[str, Any]) -> str:
    """
    First-pass result classification using nflverse structured fields

    - Start with explicit outcome flags (touchdown, interception, sack) before guessing from context
    - Keep categories small and stable; detail can come later via text/LLM
    - Provides a baseline label even when play_text parsing is deferred
    """
    # Administrative outcomes first
    if _to_int(row.get("no_play")) == 1:
        return "no_play"
    if _to_int(row.get("penalty")) == 1:
        return "penalty"

    # Big outcomes
    if _to_int(row.get("touchdown")) == 1:
        return "touchdown"
    if _to_int(row.get("interception")) == 1:
        return "interception"
    if _to_int(row.get("fumble_lost")) == 1:
        return "fumble"
    if _to_int(row.get("sack")) == 1:
        return "sack"

    # Pass outcomes (when available)
    if _to_int(row.get("incomplete_pass")) == 1:
        return "incomplete"
    if _to_int(row.get("complete_pass")) == 1:
        return "complete"

    # If we have yards but no explicit result, assume the common case
    yg = _to_int(row.get("yards_gained"))
    if yg is not None:
        # Optional nuance: some plays end out of bounds; nflverse often has out_of_bounds
        if _to_int(row.get("out_of_bounds")) == 1:
            return "out_of_bounds"
        return "tackle"

    return "other"
