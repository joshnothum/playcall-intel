from playcall_intel.mapper import infer_result


ALLOWED_RESULTS = {
    "tackle",
    "complete",
    "incomplete",
    "touchdown",
    "interception",
    "fumble",
    "sack",
    "out_of_bounds",
    "penalty",
    "no_play",
    "other",
}


def test_infer_result_returns_allowed_values():
    # Minimal representative rows (strings to mirror CSV inputs)
    rows = [
        {"yards_gained": "3"},                 # common case
        {"complete_pass": "1", "yards_gained": "8"},
        {"incomplete_pass": "1", "yards_gained": "0"},
        {"touchdown": "1", "yards_gained": "25"},
        {"interception": "1"},
        {"fumble_lost": "1"},
        {"sack": "1", "yards_gained": "-7"},
        {"out_of_bounds": "1", "yards_gained": "5"},
        {"penalty": "1"},
        {"no_play": "1"},
        {},                                    # fallback
    ]

    for r in rows:
        assert infer_result(r) in ALLOWED_RESULTS


def test_infer_result_priority_order():
    # Administrative flags should override everything else
    assert infer_result({"no_play": "1", "touchdown": "1"}) == "no_play"
    assert infer_result({"penalty": "1", "interception": "1"}) == "penalty"

    # Big outcomes should win over generic yards-based fallback
    assert infer_result({"touchdown": "1", "yards_gained": "1"}) == "touchdown"
    assert infer_result({"interception": "1", "yards_gained": "10"}) == "interception"
    assert infer_result({"fumble_lost": "1", "yards_gained": "4"}) == "fumble"
    assert infer_result({"sack": "1", "yards_gained": "-2"}) == "sack"


def test_infer_result_pass_outcomes():
    assert infer_result({"complete_pass": "1", "yards_gained": "6"}) == "complete"
    assert infer_result({"incomplete_pass": "1", "yards_gained": "0"}) == "incomplete"


def test_infer_result_common_fallbacks():
    assert infer_result({"out_of_bounds": "1", "yards_gained": "7"}) == "out_of_bounds"
    assert infer_result({"yards_gained": "0"}) == "tackle"
    assert infer_result({}) == "other"
