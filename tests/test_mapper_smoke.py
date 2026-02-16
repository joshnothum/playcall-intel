from playcall_intel.mapper import infer_play_type, row_to_play_first_pass


ALLOWED_PLAY_TYPES = {
    "run",
    "pass",
    "qb_kneel",
    "qb_spike",
    "kickoff",
    "punt",
    "field_goal",
    "extra_point",
    "two_point_attempt",
    "penalty",
    "no_play",
    "other",
}


def test_infer_play_type_returns_allowed_values():
    # Minimal representative rows (flags as strings to match CSV behavior)
    rows = [
        {"rush": "1"},
        {"pass": "1"},
        {"punt_attempt": "1"},
        {"field_goal_attempt": "1"},
        {"qb_kneel": "1"},
        {"qb_spike": "1"},
        {"penalty": "1"},
        {"no_play": "1"},
        {},  # should fall back to "other"
    ]

    for r in rows:
        assert infer_play_type(r) in ALLOWED_PLAY_TYPES


def test_row_to_play_first_pass_sets_play_type_from_infer():
    row = {
        "posteam": "ARI",
        "defteam": "NO",
        "qtr": "1",
        "down": "1",
        "ydstogo": "10",
        "yardline_100": "78",
        "yards_gained": "3",
        "rush": "1",
    }

    play = row_to_play_first_pass(row)
    assert play.play_type == "run"
